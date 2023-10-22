import os
from pathlib import Path
import struct
from indexing import PositionalInvertedIndex

class DiskIndexWriter():
    def writeIndex(self, index: PositionalInvertedIndex, savePath):
        # writeIndex will (hopefully) write an index to "disk" to be read
        # Leaving a lot of comments for now because it's confusing 
        # & need to keep working on it to fix many bugs (like multiple docs for unpacking)
        # TODO: without gaps for now
        format_dft = 'i'
        format_id_tftd = 'ii'
        format_position = 'i'

        with open(savePath, 'wb') as file:
            for term, postingsList in index.index.items():
                packed_data = b''
                dft = len(postingsList) # document frequency for term
                packed_data += struct.pack(format_dft, dft)
                for posting in postingsList:
                    docid = posting.doc_id
                    tftd = len(posting.positions) # term frequency for current doc
                    packed_data += struct.pack(format_id_tftd, docid, tftd)
                    packed_data += struct.pack(f'{len(posting.positions)}{format_position}', *posting.positions)
                file.write(packed_data)
        # calling readIndex here for testing purposes
        self.readIndex(savePath)
        
    def readIndex(self, savePath):
        # Unpacking the data for testing purposes #
        # BUG: we are only seeing the first docs info for each term
        format_dft = 'i'
        format_id_tftd = 'ii'
        format_position = 'i'
        file_path = savePath

        with open(file_path, 'rb') as file:
            packed_data = file.read()
        
        # the 4s are because storing integers which are 4 bytes
        dft = struct.unpack(format_dft, packed_data[:4])[0]
        print(f'dft: {dft}')

        # while loop, make sure packed data is long enough to unpack (otherwise at end of a doc messes up -> bug?)
        # 16 since we are storing at least 4 integers
        while len(packed_data) >= 16:
            dft = struct.unpack(format_dft, packed_data[:4])[0] # 1st byte
            docid, tftd = struct.unpack(format_id_tftd, packed_data[4:12]) # 2nd and 3rd bytes
            positions = struct.unpack(format_position * tftd, packed_data[12:12 + 4 * tftd]) # 4th byte and on depending on number of positions
            print(f'dft: {dft}, DocID: {docid}, TermFreq: {tftd}, Positions: {positions}')
            packed_data = packed_data[12 + 4 * tftd:] # to the next term
        return