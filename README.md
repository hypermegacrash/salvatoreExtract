# SalvatoreExtract

## Overview

Code for extracting PackInfo archive files as found in the following games...
- Ape Escape: Pumped & Primed
- Ape Escape: Million Monkeys

## Project Structure

```
salvatoreExtract
├───pcsx2_patch             - pnanch patches, place the contents of this folder in your PCSX2/cheats folder
|   ├───8EFDBAEB.pnach      - Million Monkeys Patches
|   └───413706BB.pnach      - Pumped & Primed Patches
├───extract_pdata_dskimg.py - Python Script for extracting files from the DSKIMG.BIN file in Million Monkeys
├───extract_pdata.py        - Python Script for extracting files from the DATA0.BIN file in Pumped & Primed
├───extract_pdata2.py       - Python Script for extracting files from the DATA2.BIN file in Pumped & Primed
├───file_def_packinfo.py    - Python Module for managing the PackInfo Archives
├───hashmap_mm_pdata1.csv   - Hashes for the file entries found in the DATA0.BIN PackInfo file for the DATA1.Bin PackData file from Million Monkeys
├───hashmap_mm_pdata3.csv   - Hashes for the file entries found in the DATA2.BIN PackInfo file for the DATA3.Bin PackData file from Million Monkeys
└───hashmap_mm_dskimg.csv   - Hashes for the file entries found in the DSKIMG.INF PackInfo file for the DSKIMG.BIN PackData file from Pumped & Primed
```

## Credits

Thanks to Gigahawk for researching PackInfo archive files and asm for printing pre hashed file names in Million Monkeys to reference.