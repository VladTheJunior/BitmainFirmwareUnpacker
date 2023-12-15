![ViewCount](https://views.whatilearened.today/views/github/VladTheJunior/BitmainFirmwareUnpacker.svg)
[![GitHub stars](https://img.shields.io/github/stars/VladTheJunior/BitmainFirmwareUnpacker)](https://github.com/VladTheJunior/BitmainFirmwareUnpacker/stargazers)
[![GitHub forks](https://img.shields.io/github/forks/VladTheJunior/BitmainFirmwareUnpacker)](https://github.com/VladTheJunior/BitmainFirmwareUnpacker/network)

# Bitmain Firmware Unpacker
*Script to unpack Bitmain .BMU firmwares (both single and merge)*


## Description

This script used to unpack BMU firmwares from Bitmain. BMU files can be 2 types: single and merge.

Merge BMU contains multiple firmwares for specific model and miner_type (eg AMLCtrl_BHB42XXX, CVCtrl_BHB42XXX, zynq7007_BHB42XXX etc.)

And Bitmain mostly distribute firmware as merge BMU.

So there is no problem with updating firmware via WEB interface, but when you try to update merge BMU via BTC Tools you will get errors like `error: 8` or `failed: Request Entity Too Large`. It happens because device uses JavaScript to automatically select required firmware from merge file, but BTC Tools doesn't. 
How to fix this? You need to unpack merge BMU with this script and then check device model and miner_type with this request:
`http://IP/cgi-bin/miner_type.cgi`

```
{"miner_type": "Antminer S19 Pro", "subtype": "CVCtrl_BHB42XXX", "fw_version": "Mon Dec 26 17:09:17 CST 2022"}
```
After that, select reqired unpacked single BMU and use it for update.

If you want to reverse content of single BMU, you can unpack it too. Note, that to check miner.pem.sig you need to use `/etc/bitmain.pub` from device.

## How To Use

1. Install Python 3 and required modules:

```
pip install -r requirements.txt
```

2. Use like this

```
(env) PS D:\Scripts\bmu> python bmu.py
usage: bmu.py [-h] {unpack,hash} ...

Operations with BMU file (both single and merge)

positional arguments:
  {unpack,hash}  Available operations
    unpack       unpack bmu file
    hash         calculate miner type hash

options:
  -h, --help     show this help message and exit
```

## Examples

Unpacking merge BMU:

```
(env) PS D:\Scripts\bmu> python bmu.py unpack .\Antminer-S19j-Pro-merge-release-20221226125147.bmu
Detected merge BMU file...


Header:

magic: abababab
version: 0
header size: 36
item count: 10
item size: 172
data offset: 16384
crc32: e41d18af
reserve0: 0x0
reserve1: 0x0

checksum passed: True

Model              Hardware           Chip    Name                                               Offset      Size  Checksum
-----------------  -----------------  ------  ----------------------------------------------  ---------  --------  ----------
Antminer S19j Pro  CVCtrl_BHB42XXX            update.bmu                                          16384  12568671  fb3fc013
Antminer S19j Pro  zynq7007_BHB42XXX          update.bmu                                       12585055  18011759  b2fe01a8
Antminer S19j Pro  AMLCtrl_BHB42XXX           update.bmu                                       30596814  12798976  7ed0c314
Antminer S19j Pro  BBCtrl_BHB42XXX            update.bmu                                       43395790  10799636  e77cddf7
Antminer S19j Pro  AMLCtrl_BHB42601           update.bmu                                       54195426  12798976  4b2412a5
Antminer S19j Pro  BBCtrl_BHB42601            update.bmu                                       66994402  10799656  3cb2fa92
Antminer S19j Pro  zynq7007_BHB42601          update.bmu                                       77794058  18011632  cfb757d7
Antminer S19j Pro  zynq7007                   Antminer-BHB42XXX-release-202212261709.bmu       95805690  18011759  b2fe01a8
Antminer S19j Pro  BBCtrl                     Antminer-BHB42XXX-BB-release-202212261719.bmu   113817449  10799636  e77cddf7
Antminer S19j Pro  AMLCtrl                    Antminer-BHB42XXX-AML-release-202212261710.bmu  124617085  12798976  7ed0c314
```

Unpacking single BMU:

```
(env) PS D:\Scripts\bmu> python bmu.py unpack '.\Antminer S19j Pro\CVCtrl_BHB42XXX\update.bmu'
Detected single BMU file...


Header:

magic: 26
miner type hash: 883b7c5d69fe738b
content: 1110000000000000
file count: 3
bmu file size: 12568671
miner.pem len: 451
miner.pem:
-----BEGIN PUBLIC KEY-----
MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAsUfS8TNhRvGrbwBiLAZJ
F/K7hPxdJbPnALrq+KBbHwm04sW4k2C8QM0hexlp2Ey1/35a2qUg/9Nj/2+wTJNZ
aSIynDLuNchD0v76XykQwIG7G2kN6osuyU3Gu8pWKkW806XN+fueT4aaYWS4296G
4MzpmpSBFDvLxeA4blqc576eya/a2oOev8C0juYfQmZp9ZvjQzJ7RXS3jmKadiBA
HIQ9ZdouiJaSZSV94XAcbV37nFgHtZKDJxdhq187fujxM91xapegT6PPAmmRtuaK
gFxgL/QGWfz5nmmuH0zDZu7Tiwy4cN8lZHsBUqPtVZdj1lp9IBybTHeIC0aamhVp
3wIDAQAB
-----END PUBLIC KEY-----

miner.pem.sig:
b'7aff303e11df256b828bbea468f5dde5577dd55a43b8f607277e41304f3f301b5581ae1a5bf8dcb0cbaf385ec2c10436de3057fbe379c512e6832c4562b7e99b00731501dc20b723d79d9dbe1ee84dd4fc54024992b0fc862f402fbbf592d52359bc85cb6e7184876aa2bf769b1db0ca3ad6ccd6d2b72329500afce391315fc66aaaf6e989e3b0e700ceafc68ea32a27ba11fd025c8cd0a8cea7e3fa6013110f6f3606c4e6c7d80435feeeca3ac3dec69ede72cdabf64d7e25416f237e89aa91c6b52960b2bcb8795f2b2c5bec9df2eb25eedc0a9bdcd7a6d9c287b255fe89ae5fd145675bfbd295ce8dc47e09c148f341e0707aa944aaa511fd4c57c0c3a5e5'

'miner.pem' and 'miner.pem.sig' extracted!

# for CV183X platform update, file description:
# BOOT.bin --------> minerfs.gz ---> /dev/mmcblk0p3
# devicetree.dtb --> sig.bin    ---> /dev/mmcblk0p4
# uImage ----------> boot.emmc  ---> /dev/mmcblk0p1

Extracting files...
  #    Code  Name              Offset     Size
---  ------  --------------  --------  -------
  0       0  BOOT.bin            2048  7896208
  1       1  devicetree.dtb   7898256     2933
  2       2  uImage           7901189  4666458

Extracting file signatures...
  #    Code  Name                  Offset    Size
---  ------  ------------------  --------  ------
  0       0  BOOT.bin.sig        12567647     256
  1       1  devicetree.dtb.sig  12567903     256
  2       2  uImage.sig          12568159     256

Verifying files...
BOOT.bin verification passed: True
devicetree.dtb verification passed: True
uImage verification passed: True

bmu.sig:
b'0e237359aab3bc6ecbaf22709b386ba721bfe7510ce897784364f98fa01bf22b6679ba875d0e55ac32003a4eeae7ce9e6752a43ca21bff238dd59c4a24c251d3ec4348c97ad84489502e08bdce85805ecdee27228dbf996582fe7ac406afb78c0375e43834cab2eb0e98be0e4ce80b7f506dac8e6623a60a99de027fdde9946bc38b1ff9cfdd1151a416ad06d977704c4360374c041327803ec155ee72b19444c210fea3a1c8edc7f9781e74beba9691ad362a7c2925d2a9f7168ba8258fb5f3665e630a567f64b0791dee76dbaba1a94559fd67e411c448e3242f567941bc2293bf7d57c1090200265099b899cb496f3900651daceb4071259ff28262bd06f5'

bmu verification passed: True
```