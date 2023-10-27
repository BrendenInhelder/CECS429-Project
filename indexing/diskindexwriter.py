import os
from pathlib import Path
import struct
from indexing import PositionalInvertedIndex

class DiskIndexWriter():
    def writeIndex(self, index: PositionalInvertedIndex, savePath):
        # writeIndex will (hopefully) write an index to "disk" to be read
        # Leaving a lot of comments for now because it's confusing 
        # TODO: Gaps and vocabulary
        bin_format = 'i'

        with open(savePath, 'wb') as index_on_disk_file:
            for term, postingsList in index.index.items():
                # packed_data = b''
                dft = len(postingsList) # document frequency for term
                packed_data = struct.pack(bin_format, dft)
                index_on_disk_file.write(packed_data)
                for posting in postingsList:
                    docid = posting.doc_id
                    packed_data = struct.pack(bin_format, docid)
                    index_on_disk_file.write(packed_data)

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