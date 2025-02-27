
# Module for managing the PackInfo Archives as seen in Pumped & Primed and Million Monkeys

import os
import csv
import gzip

PACKTYPE_PAP_DISIMG = 0
PACKTYPE_MM_PDATA1  = 1
PACKTYPE_MM_PDATA3  = 2

HASHMAP_PAP_DISIMG = os.path.join(os.path.dirname(__file__), "hashmap_pap_dskimg.csv")
HASHMAP_MM_PDATA1  = os.path.join(os.path.dirname(__file__), "hashmap_mm_pdata1.csv")
HASHMAP_MM_PDATA3  = os.path.join(os.path.dirname(__file__), "hashmap_mm_pdata3.csv")

# Recreation of the hash function as seen in Pumped & Primed and Million Monkeys
def gen_hash(in_path):
    out_hash = 0
    for char in in_path:
        out_hash = (out_hash * 0x25) + ord(char)
        out_hash &= 0xFFFFFFFF # Mask for only 32 bits / signed 4 byte integer
    return out_hash

# Responsible for managing the dictionary key value pairs for pre hash and hashed names
class HashMapMgr:
    def __init__(self):
        self.hash_map = {}

    # Extract the hash map containing a list of pre hashed names and their hashes
    def extract_hash_map(self, in_hashmap_path):
        with open(in_hashmap_path) as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                self.hash_map[int(row["hash"], 16)] = row["name"]

    # Save the hashmap to the host filesystem for later use.
    def save_hash_map_to_fs(self, out_hashmap_path):
        with open(out_hashmap_path, "w") as outFile:
            outFile.write(f"hash,name\n")
            for key in self.hash_map.keys():
                outFile.write(f"{key:08x},{self.hash_map[key]}\n")

# Responsible for a single entry found in the PackInfo Index File
class PackInfoEntry:
    def __init__(self):
        # Struct definition
        self.nNameHash     = 0 # 0x00 - The hashed name calculated by the custom hashing function
        self.nSectorOffset = 0 # 0x04 - Multiply by 0x800 to get the correct offset into the file
        self.nSize         = 0 # 0x08 - Size of the packdata entry

        # Non structure variables
        self.preHashName   = ""   # For when printing pre hashed names
        self.compressed    = True # Pumped & Primed has some non gzipped entries

    # Read in an entry from the index file
    def read(self, in_packdata_file):
        self.nNameHash     = int.from_bytes(in_packdata_file.read(4), "little")
        self.nSectorOffset = int.from_bytes(in_packdata_file.read(4), "little")
        self.nSize         = int.from_bytes(in_packdata_file.read(4), "little")

    # Check for gzip magic at the start of the entry
    def isEntryCompressed(self, in_packdata_file):
        in_packdata_file.seek(self.nSectorOffset * 0x800, 0)
        headercheck = int.from_bytes(in_packdata_file.read(2), "little")
        
        if(headercheck == 0x8B1F): self.compressed = True
        else:                      self.compressed = False

    def extractToFS(self, in_packdata_file, out_path):
        if self.nSize == 0: return

        in_packdata_file.seek(self.nSectorOffset * 0x800, 0)

        if(self.compressed):
            gzip_data = in_packdata_file.read(self.nSize)
            decompressed_data = gzip.decompress(gzip_data)
        else:
            decompressed_data = in_packdata_file.read(self.nSize)

        if self.preHashName:
            filePath = f"{out_path}/{self.preHashName}"
        else:
            filePath = f"{out_path}/{self.nNameHash:08x}.BIN"

        if not os.path.exists(os.path.dirname(filePath)):
            os.makedirs(os.path.dirname(filePath))

        fout = open(filePath, "wb")
        fout.write(decompressed_data)
        fout.close()

    # The size of a PackInfoEntry should be 12 bytes long
    def getSize(): return int(0x0C)

    # Debug print the variables for this entry
    def print(self):
        print(f"NameHash: 0x{self.nNameHash:08x} nSectorOffset: {self.nSectorOffset:8} nSize: {self.nSize:8} Name: {self.preHashName:60} GZip Compressed: {self.compressed}")

# Read a PackInfo file into an array of PackInfoEntry entries
def readPackInfoFile(in_packinfo_file):
    out_packinfo_entries = []

    index_file_handle = open(in_packinfo_file, 'rb')
    index_size = os.path.getsize(in_packinfo_file)
    index_entry_count = int(index_size / PackInfoEntry.getSize())

    for idx in range(index_entry_count):
        thisEntry = PackInfoEntry()
        thisEntry.read(index_file_handle)

        out_packinfo_entries.append(thisEntry)

    return out_packinfo_entries

# Test a text file full of potential hash names against an array of PackInfo entries
def test_hashnames(in_testnames_filepath, in_packinfo_array):
    if not os.path.exists(in_testnames_filepath):
        print(f"Could not find {in_testnames_filepath}, skipping!")
        return
    
    test_hashmap = {}
    with open(in_testnames_filepath, encoding="utf-8") as f:
        lines = f.read().splitlines()
        for line in lines:
            test_hashmap[gen_hash(line)] = line

    for thisEntry in in_packinfo_array:
        if thisEntry.preHashName: continue # Dont waste our time checking for names we already got
        if (thisEntry.nNameHash in test_hashmap.keys()):
            thisEntry.preHashName = test_hashmap[thisEntry.nNameHash]

# The meat of the module, call this to extract assets from a provided packdata and PackInfo
def extract_monkey_assets(packinfo_filepath, packdata_filepath, hashmap_filetype, outdata_filePath=None, testnames_filepath=None):
    # First. Get our PackInfo array of entries
    aPackInfo = readPackInfoFile(packinfo_filepath)
    
    # Second, get our hashmap for hash names
    hashMgr = HashMapMgr()
    if   hashmap_filetype == PACKTYPE_PAP_DISIMG: hashMgr.extract_hash_map(HASHMAP_PAP_DISIMG)
    elif hashmap_filetype == PACKTYPE_MM_PDATA1:  hashMgr.extract_hash_map(HASHMAP_MM_PDATA1)
    elif hashmap_filetype == PACKTYPE_MM_PDATA3:  hashMgr.extract_hash_map(HASHMAP_MM_PDATA3)
    else:
        print("Unknown PackInfo Revision!!! Stopping.")
        return

    # Third, get our hash names if we have any, also testing for new ones if needed!
    for thisEntry in aPackInfo:
        if (thisEntry.nNameHash in hashMgr.hash_map.keys()):
            thisEntry.preHashName = hashMgr.hash_map[thisEntry.nNameHash]

    if testnames_filepath:
        test_hashnames(testnames_filepath, aPackInfo)

    # Fourth, get our corresponding packdata file
    packdata = open(packdata_filepath, 'rb')

    for entry in aPackInfo:
        entry.isEntryCompressed(packdata)

    # Fifth, print the status of our output to the user
    for entry in aPackInfo:
        entry.print()

    if not outdata_filePath:
        if   hashmap_filetype == PACKTYPE_PAP_DISIMG: outdata_filePath = "OUT_DSKIMG"
        elif hashmap_filetype == PACKTYPE_MM_PDATA1:  outdata_filePath = "OUT_PDATA1"
        elif hashmap_filetype == PACKTYPE_MM_PDATA3:  outdata_filePath = "OUT_PDATA3"
        
    # Finally, extract the contents to the file system
    print(f"Writting out assets to {outdata_filePath}, please wait...")
    for entry in aPackInfo:
        entry.extractToFS(packdata, outdata_filePath)
    print("DONE!")

    # To wrap it up, close our file references and update our hashmap if needed
    packdata.close()

    for thisEntry in aPackInfo:
        if (thisEntry.nNameHash in hashMgr.hash_map.keys()):
            hashMgr.hash_map[thisEntry.nNameHash] = thisEntry.preHashName

    if   hashmap_filetype == PACKTYPE_PAP_DISIMG: hashMgr.save_hash_map_to_fs(HASHMAP_PAP_DISIMG)
    elif hashmap_filetype == PACKTYPE_MM_PDATA1:  hashMgr.save_hash_map_to_fs(HASHMAP_MM_PDATA1)
    elif hashmap_filetype == PACKTYPE_MM_PDATA3:  hashMgr.save_hash_map_to_fs(HASHMAP_MM_PDATA3)