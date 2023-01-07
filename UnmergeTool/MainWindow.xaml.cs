using Microsoft.Win32;
using System;
using System.Collections.Generic;
using System.Collections.ObjectModel;
using System.ComponentModel;
using System.Diagnostics;
using System.Drawing;
using System.IO;
using System.Linq;
using System.Reflection.PortableExecutable;
using System.Runtime.CompilerServices;
using System.Text;
using System.Threading.Tasks;
using System.Windows;
using System.Windows.Automation;
using System.Windows.Controls;
using System.Windows.Data;
using System.Windows.Documents;
using System.Windows.Forms;
using System.Windows.Input;

using UnmergeTool;
using MessageBox = System.Windows.MessageBox;
using OpenFileDialog = Microsoft.Win32.OpenFileDialog;

namespace UnmergeTool
{
    /// <summary>
    /// Interaction logic for MainWindow.xaml
    /// </summary>
    public partial class MainWindow : Window, INotifyPropertyChanged
    {
        public event PropertyChangedEventHandler PropertyChanged;
        private void NotifyPropertyChanged([CallerMemberName] String propertyName = "")
        {
            PropertyChanged?.Invoke(this, new PropertyChangedEventArgs(propertyName));
        }
        private ObservableCollection<MergeUpgrade> mergeUpgrades = new ObservableCollection<MergeUpgrade>();
        public ObservableCollection<MergeUpgrade> MergeUpgrades
        {
            get { return mergeUpgrades; }
            set
            {
                mergeUpgrades = value;
                NotifyPropertyChanged();
            }
        }

        private string filePath = null;
        public string FilePath
        {
            get { return filePath; }
            set
            {
                filePath = value;
                NotifyPropertyChanged();
                NotifyPropertyChanged("FileName");
            }
        }

        public string FileName
        {
            get
            {
                return Path.GetFileName(filePath);
            }
        }

        public MainWindow()
        {
            InitializeComponent();
            DataContext = this;


        }

        private void CheckBox_Checked(object sender, RoutedEventArgs e)
        {
            foreach (var upgrade in MergeUpgrades)
            {
                upgrade.IsChecked = true;
            }
        }

        private void CheckBox_Unchecked(object sender, RoutedEventArgs e)
        {
            foreach (var upgrade in MergeUpgrades)
            {
                upgrade.IsChecked = false;
            }
        }

        private void CheckBox_Checked_1(object sender, RoutedEventArgs e)
        {
            cbAll.Checked -= CheckBox_Checked;
            cbAll.Unchecked -= CheckBox_Unchecked;
            cbAll.IsChecked = MergeUpgrades.Count(x => x.IsChecked == false) == 0;
            cbAll.Checked += CheckBox_Checked;
            cbAll.Unchecked += CheckBox_Unchecked;
        }

        private void CheckBox_Unchecked_1(object sender, RoutedEventArgs e)
        {
            cbAll.Checked -= CheckBox_Checked;
            cbAll.Unchecked -= CheckBox_Unchecked;
            cbAll.IsChecked = MergeUpgrades.Count(x => x.IsChecked == false) == 0;
            cbAll.Checked += CheckBox_Checked;
            cbAll.Unchecked += CheckBox_Unchecked;
        }

        private void MenuItem_Click(object sender, RoutedEventArgs e)
        {
            mainMenu.IsEnabled = false;
            OpenFileDialog openFileDialog = new OpenFileDialog();
            openFileDialog.Filter = "Bitmain Merged Upgrades .BMU files (*.bmu)|*.bmu";
            if (openFileDialog.ShowDialog() == true)
            {
                FilePath = openFileDialog.FileName;
            }
            else
            {
                mainMenu.IsEnabled = true;
                return;
            }

            try
            {
                MergeUpgrades.Clear();
                using var file = File.OpenRead(FilePath);
                using var reader = new BinaryReader(file);
                uint magic = reader.ReadUInt32();
                if (magic != 0xabababab)
                    throw new Exception("File is not a valid Bitmain Merged Upgrades file");
                reader.ReadInt32(); // 0
                reader.ReadInt32(); // ?
                int firmwaresCount = reader.ReadInt32();
                reader.ReadInt32(); // blockSize
                reader.ReadInt32(); // start offset
                reader.ReadInt32(); // overall size
                reader.ReadInt64(); // 0
                for (int i = 0; i < firmwaresCount; i++)
                {
                    ushort fileNameLength = reader.ReadUInt16();
                    byte controlTypeLength = reader.ReadByte();
                    byte modelLength = reader.ReadByte();
                    string fileName = Encoding.UTF8.GetString(reader.ReadBytes(fileNameLength));
                    reader.ReadBytes(96 - fileNameLength); // padding
                    string controlType = Encoding.UTF8.GetString(reader.ReadBytes(controlTypeLength));
                    reader.ReadBytes(32 - controlTypeLength); // padding
                    string model = Encoding.UTF8.GetString(reader.ReadBytes(modelLength));
                    reader.ReadBytes(32 - modelLength);  // padding
                    uint offset = reader.ReadUInt32();

                    uint size = reader.ReadUInt32();
                    MergeUpgrade upgrade = new MergeUpgrade();
                    upgrade.Model = model;
                    upgrade.ControlType = controlType;
                    upgrade.Size = size;
                    upgrade.Offset = offset;
                    MergeUpgrades.Add(upgrade);
                }
                foreach (var upgrade in MergeUpgrades)
                {

                    reader.BaseStream.Seek(upgrade.Offset, SeekOrigin.Begin);
                    byte[] data = reader.ReadBytes((int)upgrade.Size);
                    upgrade.Hash = K4os.Hash.xxHash.XXH32.DigestOf(data); //Crc32Algorithm.Compute(data);
                }

            }
            catch (Exception exp)
            {
                MessageBox.Show(exp.Message, "Error", MessageBoxButton.OK, MessageBoxImage.Error);
            }
            mainMenu.IsEnabled = true;
        }

        private async void MenuItem_Click_1(object sender, RoutedEventArgs e)
        {
            mainMenu.IsEnabled = false;
            if (MergeUpgrades.Count(x => x.IsChecked) == 0)
            {
                MessageBox.Show("No file is selected for extraction!", "Warning", MessageBoxButton.OK, MessageBoxImage.Warning);
                mainMenu.IsEnabled = true;
                return;
            }

            using (FolderBrowserDialog dialog = new())
            {
                DialogResult result = dialog.ShowDialog();

                if (result == System.Windows.Forms.DialogResult.OK)
                {
                    try
                    {
                        using var file = File.OpenRead(FilePath);
                        using var reader = new BinaryReader(file);
                        uint magic = reader.ReadUInt32();
                        if (magic != 0xabababab)
                            throw new Exception("File is not a valid Bitmain Merge Upgrade file");
                        foreach (var upgrade in MergeUpgrades)
                        {
                            if (upgrade.IsChecked)
                            {
                                file.Seek(upgrade.Offset, SeekOrigin.Begin);
                                var data = new byte[upgrade.Size];
                                await file.ReadAsync(data, 0, (int)upgrade.Size);
                                await File.WriteAllBytesAsync(Path.Join(dialog.SelectedPath, $"{upgrade.Model}-{upgrade.ControlType}-xxh32={upgrade.Hash.ToString("X8").ToLower()}.bmu"), data);
                            }
                        }
                    }
                    catch (Exception exp)
                    {
                        MessageBox.Show(exp.Message, "Error", MessageBoxButton.OK, MessageBoxImage.Error);
                    }
                }
            }
            mainMenu.IsEnabled = true;
        }

        private void MenuItem_Click_2(object sender, RoutedEventArgs e)
        {
            string targetURL = "https://github.com/VladTheJunior/UnmergeTool";
            var psi = new ProcessStartInfo
            {
                FileName = targetURL,
                UseShellExecute = true
            };
            Process.Start(psi);
        }

        private void MenuItem_Click_3(object sender, RoutedEventArgs e)
        {
            About about = new About();
            about.ShowDialog();
        }
    }
}
