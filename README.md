![ViewCount](https://views.whatilearened.today/views/github/VladTheJunior/UnmergeTool.svg)
[![GitHub stars](https://img.shields.io/github/stars/VladTheJunior/UnmergeTool)](https://github.com/VladTheJunior/UnmergeTool/stargazers)
[![GitHub forks](https://img.shields.io/github/forks/VladTheJunior/UnmergeTool)](https://github.com/VladTheJunior/UnmergeTool/network)
[![GitHub issues](https://img.shields.io/github/issues/VladTheJunior/UnmergeTool)](https://github.com/VladTheJunior/UnmergeTool/issues)
[![GitHub license](https://img.shields.io/github/license/VladTheJunior/UnmergeTool)](https://github.com/VladTheJunior/UnmergeTool/blob/master/LICENSE)
<!-- PROJECT LOGO -->
<br />
<p align="center">
  <a href="https://github.com/VladTheJunior/UnmergeTool">
    <img src="Images/Icon.png" alt="Logo">
  </a>
</p>

# Unmerge Tool

*Утилита для распаковки merge прошивок Bitmain Upgrades .BMU*

**Developer:** VladTheJunior<br />
**Current version:** 0.0.1<br />

[Download Portable (.ZIP archive)]()<br />

*__Note__: Portable version may require .NET6 desktop runtime: https://dotnet.microsoft.com/en-us/download/dotnet/6.0*


Объединенные (merge) прошивки содержат прошивки для определенной модели устройства с разными типами контрольных плат. Названия таких прошивок выглядят примерно так: __Antminer-S19-merge-release-20211216091201-8IN1__. 

Важно понимать, что при обновлении через веб-интерфейс загружается не весь merge файл, а только та часть, которая содержит прошивку, подходящую для контрольной платы этого устройства.

При попытке обновления merge прошивки через BTCTool или APMinerTool на устройство загружается весь файл, поэтому происходит ошибка обновления (из-за большого размера файла, или ошибки распознавания).

Поэтому чтобы обновлять устройства через эти программы, нужно сначала распаковать merge файл и выбрать прошивку с подходящим типом контрольной платы.
Для того, чтобы точно определить модель контрольной платы, нужно ввести в адресной строке браузера:

```http://IP address/cgi-bin/miner_type.cgi```

В ответ получим следующее:

```{"miner_type": "Antminer S19j Pro", "subtype": "AMLCtrl_BHB42601", "fw_version": "Fri Oct 15 11:12:06 CST 2021"}```

где subtype это тип контрольной платы.




