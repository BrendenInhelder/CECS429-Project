import os
from pathlib import Path
import sqlite3
import struct
from indexing import PositionalInvertedIndex

class DiskIndexWriter():
    def writeIndex(self, index: PositionalInvertedIndex, savePath):
        # writeIndex will write an index to "disk" to be read
        # TODO: vocabulary...might work properly?
        # setup the db for the vocab
        vocabConnection = sqlite3.connect("vocabulary.db")
        cursor = vocabConnection.cursor()
        cursor.execute("CREATE TABLE IF NOT EXISTS vocab (term TEXT PRIMARY KEY, byte INTEGER)")
        vocabConnection.commit()

        bin_format = 'i'
        with open(savePath, 'wb') as index_on_disk_file:
            for term, postingsList in index.index.items():
                # first we store the terms byte location
                insert_structure = "INSERT INTO vocab (term, byte) VALUES (?, ?)"
                cursor.execute(insert_structure, (term, index_on_disk_file.tell()))
                vocabConnection.commit()

                dft = len(postingsList) # document frequency for term
                packed_data = struct.pack(bin_format, dft)
                index_on_disk_file.write(packed_data)
                prevDoc = 0
                for posting in postingsList:
                    docid = posting.doc_id - prevDoc
                    packed_data = struct.pack(bin_format, docid)
                    index_on_disk_file.write(packed_data)
                    prevDoc = docid

                    tftd = len(posting.positions) # term frequency for current doc
                    packed_data = struct.pack(bin_format, tftd)
                    index_on_disk_file.write(packed_data)
                    
                    prevPos = 0
                    for pos in posting.positions:
                        packed_data = struct.pack(bin_format, pos-prevPos)
                        index_on_disk_file.write(packed_data)
                        prevPos = pos
        
    def readIndex(self, savePath):
        # Unpacking the data for testing purposes #
        bin_format = 'i'
        print("Reading from binary file:")
        with open(savePath, 'rb') as index_on_disk_file:
            while True:
                packed_data = index_on_disk_file.read(4)
                if not packed_data:
                    break
                unpacked_data = struct.unpack(bin_format, packed_data)[0]
                print(unpacked_data, end=' ')
        return