
# Script for extracting a file from the DSKIMG.BIN archive in Ape Escape: Pumped and Primed

from file_def_packinfo import *

# Ape Escape Pumped and Primed Assets
packinfo_filepath = f"DSKIMG/DSKIMG.INF"
packdata_filepath = f"DSKIMG/DSKIMG.BIN"

if __name__ == '__main__':
    if not os.path.exists(packinfo_filepath) and not os.path.exists(packdata_filepath):
        print(f"Unable to find {packinfo_filepath} and {packdata_filepath}!")
        print("Extract DSKIMG.BIN & DSKIMG.INF from the root of your Ape Escape Pumped and Primed copy, " +
              "create a folder named DSKIMG in the same folder as this script and place the files within.")
        input("Press Enter to continue...")
        exit()

    extract_monkey_assets(packinfo_filepath, packdata_filepath, PACKTYPE_PAP_DISIMG)
    input("Press Enter to continue...")