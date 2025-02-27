
# Script for extracting a file from the PDATA2.BIN archive in Ape Escape: Million Monkeys

from file_def_packinfo import *

# Ape Escape Million Monkeys Audio
packinfo_filepath = f"PDATA/DATA2.BIN"
packdata_filepath = f"PDATA/DATA3.BIN"

if __name__ == '__main__':
    if not os.path.exists(packinfo_filepath) and not os.path.exists(packdata_filepath):
        print(f"Unable to find {packinfo_filepath} and {packdata_filepath}!")
        print("Extract the PDATA folder from your copy of Ape Escape Million Monkeys and place it in this same folder.")
        input("Press Enter to continue...")
        exit()

    extract_monkey_assets(packinfo_filepath, packdata_filepath, PACKTYPE_MM_PDATA3)
    input("Press Enter to continue...")