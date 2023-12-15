import binascii
import struct
from pathlib import Path
from Crypto.PublicKey import RSA
from Crypto.Signature import PKCS1_v1_5
from Crypto.Hash import SHA256
import argparse
from tabulate import tabulate
from farmhash import Fingerprint64


          
def get_file_name(code, is_sign):
    if code == 0:
        file_name = "BOOT.bin"
    elif code == 1:
        file_name = "devicetree.dtb"
    elif code == 2:
        file_name = "uImage"
    elif code == 3:
        file_name = "minerfs.image.gz"
    elif code == 4:
        file_name = "update.image.gz"
    elif code == 5:
        file_name = "crl.tar.gz"
    elif code == 6:
        file_name = "miner.btm.tar.gz"
    elif code == 7:
        file_name = "reserve"
    elif code == 9:
        file_name = "datafile"       

    if is_sign:
        file_name+=".sig"

    return file_name


def check_miner_pem(bitmain_pub, miner_pem, miner_pem_sig):
    with open(bitmain_pub, 'rb') as p:
        public_key = RSA.importKey(p.read())

    signer = PKCS1_v1_5.new(public_key)
    digest = SHA256.new()
    digest.update(miner_pem)

    return signer.verify(digest, miner_pem_sig)



def unpack_single(file):
    directory = Path("output")
    directory.mkdir(parents=True, exist_ok=True)
    data = file.read()
    overall_file_size = len(data)
    if overall_file_size >= 2048:
        file.seek(0)
        header_data = file.read(2048)
        magic = header_data[0]
        print("\nHeader:\n")
        print(f"magic: {magic:x}")
        if magic != 38:
            print('Not valid BMU file')
            return            
        bmu_miner_type_hash = struct.unpack('Q', header_data[2:10])[0]
        content = struct.unpack('>H', header_data[11:11+2])[0]
        file_count = int.bit_count(content)
        print(f"miner type hash: {bmu_miner_type_hash:x}")
        print(f"content: {content:b}")
        print(f"file count: {file_count}")

        if file_count != header_data[1304]:
            print("file count check not passed!")
            return

        file_sum_size = (header_data[1304] + 9) << 8
        exact_file_size = struct.unpack('>I', header_data[1305:1305+4])[0] # zero
        
        for i in range(0, file_count):
            file_size = struct.unpack('>I', header_data[5 * i + 1310:5 * i + 1310+4])[0]
            file_sum_size += file_size
                
        print(f"bmu file size: {file_sum_size}")

        if overall_file_size != file_sum_size:
            print("file size check not passed!")
            return   

                
        miner_pem_len = struct.unpack('>H', header_data[22:22+2])[0]
        miner_pem = header_data[24:24+miner_pem_len]
        miner_pem_sig = header_data[1048:1048+256]

        print(f"miner.pem len: {miner_pem_len}")       
        print(f"miner.pem:\n{miner_pem.decode('utf-8')}")   
        print(f"miner.pem.sig:\n{binascii.hexlify(miner_pem_sig)}") 
        #is_verified = check_miner_pem(bitmain_pub, miner_pem, miner_pem_sig)

        with open(Path(directory, 'miner.pem'), 'wb') as miner_pem_file:
            miner_pem_file.write(miner_pem)
        with open(Path(directory, 'miner.pem.sig'), 'wb') as miner_pem_sig_file:
            miner_pem_sig_file.write(miner_pem_sig)

        print(f"\n'miner.pem' and 'miner.pem.sig' extracted!\n")    

        digest = SHA256.new()
        digest.update(header_data)

        check = bytearray(digest.digest())

        print("# for CV183X platform update, file description:\n"\
        "# BOOT.bin --------> minerfs.gz ---> /dev/mmcblk0p3\n"\
        "# devicetree.dtb --> sig.bin    ---> /dev/mmcblk0p4\n"\
        "# uImage ----------> boot.emmc  ---> /dev/mmcblk0p1\n")

        files = []
        print("Extracting files...")
        for i in range(0, file_count):
            file_size = struct.unpack('>I', header_data[5 * i + 1310:5 * i + 1310+4])[0]
            file_code = header_data[5 * i + 1309]
            file_name = get_file_name(file_code, False)

            files.append(( i, file_code, file_name, file.tell(), file_size))

            with open(Path(directory, file_name), "wb") as inner_file:
                content = file.read(file_size)
                inner_file.write(content)
        
            digest = SHA256.new()
            digest.update(content)   
            c = digest.digest()
            check.extend(c)

        print(tabulate(files, headers=('#', 'Code', 'Name', 'Offset', 'Size')))
        print()
        
        sig_files = []
        print("Extracting file signatures...")
        for i in range(0, file_count):
            file_code = header_data[5 * i + 1309]  
            file_name = get_file_name(file_code, True) 
            sig_files.append((i, file_code, file_name, file.tell(), 256))
            content_signature = file.read(256)  
            with open(Path(directory, file_name), "wb") as inner_file:
                inner_file.write(content_signature)
            digest = SHA256.new()
            digest.update(content_signature)   
            c = digest.digest()
            check.extend(c)
        print(tabulate(sig_files, headers=('#', 'Code', 'Name', 'Offset', 'Size')))
        print()
        miner_pem_key = RSA.importKey(miner_pem) 
        signer = PKCS1_v1_5.new(miner_pem_key)
        print("Verifying files...")
        for i in range(0, file_count):
            file.seek(files[i][3])
            digest = SHA256.new()
            digest.update(file.read(files[i][4])) 
            file.seek(sig_files[i][3])
            signature = file.read(256)
            is_file_verified = signer.verify(digest, signature)
            print(f"{files[i][2]} verification passed: {is_file_verified}")
        print()

        count = (file_count << 6) + 32     

        digest = SHA256.new()
        digest.update(check[:count])   

        file.seek(-256,2)
        signature = file.read(256)

        print(f"bmu.sig:\n{binascii.hexlify(signature)}\n") 

        with open(Path(directory, "bmu.sig"), "wb") as inner_file:
            inner_file.write(signature)

        is_bmu_verified = signer.verify(digest, signature)

        print(f"bmu verification passed: {is_bmu_verified}")

    else:
        print(f"File size is lower than 2048!")



def unpack_merge(file):
    data = bytearray(file.read())
    file.seek(0)
    header = file.read(36)

    magic, version, header_size, item_count, item_size, data_offset, crc32, reserve0, reserve1 = struct.unpack(
        'IIIIIIIII', header)

    print("\nHeader:\n")
    print(f"magic: {magic:x}")
    print(f"version: {version}")
    print(f"header size: {header_size}")
    print(f"item count: {item_count}")
    print(f"item size: {item_size}")
    print(f"data offset: {data_offset}")
    print(f"crc32: {crc32:x}")
    print(f"reserve0: {hex(reserve0)}")
    print(f"reserve1: {hex(reserve1)}")
    print()
    if magic != 0xABABABAB:
        print('Not valid merge file')
        return

    data[24] = 0
    data[25] = 0
    data[26] = 0
    data[27] = 0

    check_crc32 = binascii.crc32(data)

    print(f'checksum passed: {check_crc32 == crc32}\n')

    # size 16 * 1024 bytes, zero padding
    firmwares = []
    for _ in range(item_count):
        firmwares.append(struct.unpack(
            'BBBB64s32s32s32sII', file.read(item_size)))

    result=[]
    for firmware in firmwares:
        filename_length, chip_length, hardware_length, model_length, filename, chip, hardware, model, offset, size = firmware
        file.seek(offset)
        data = file.read(size)

        directory = Path(model[:model_length].decode(
            "utf-8"), hardware[:hardware_length].decode("utf-8"), chip[:chip_length].decode("utf-8"))
        directory.mkdir(parents=True, exist_ok=True)
        firmware_name = Path(directory, filename[:filename_length].decode("utf-8"))

        with open(firmware_name, 'wb') as firmware_file:
            firmware_file.write(data)
        crc = f'{binascii.crc32(data):x}'
        result.append((model[:model_length].decode("utf-8"), hardware[:hardware_length].decode("utf-8") ,chip[:chip_length].decode("utf-8"), filename[:filename_length].decode("utf-8") ,offset,size,crc))
    print(tabulate(result, headers=('Model', 'Hardware', 'Chip', 'Name', 'Offset', 'Size', 'Checksum')))



def unpack(path):
    with open (path, 'rb') as file:
        data = file.read(4)
        file.seek(0)
        if data[0] == 38:
            print("Detected single BMU file...\n")
            unpack_single(file)
        elif data == b'\xab\xab\xab\xab':
            print("Detected merge BMU file...\n")
            unpack_merge(file)
        else:
            print("Not valid bmu file!")

def main():
    parser = argparse.ArgumentParser(description='Operations with BMU file (both single and merge)')
    subparsers = parser.add_subparsers(dest='operation', help='Available operations')
    unpack_parser = subparsers.add_parser('unpack', help='unpack bmu file')
    hash_parser = subparsers.add_parser('hash', help='calculate miner type hash')
    unpack_parser.add_argument('file',  type=str)
    hash_parser.add_argument('string',  type=str)
 
    args = parser.parse_args()
    if args.operation == 'unpack':
        unpack(args.file)
    elif args.operation == "hash":
        print(f"Miner type hash[{args.string}]: {Fingerprint64(args.string):x}")
    else:
        parser.print_help()


if __name__ == "__main__":
    main()