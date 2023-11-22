import struct
from typing import Iterable
from .postings import Posting
from .index import Index
from pathlib import Path
import sqlite3

class DiskPositionalIndex(Index):
    """Implements an Index using an inverted index that exists on Disk. 
    It Is constructed in a binary file and this class retrieves them."""

    def __init__(self, index_path : Path, vocab_path : Path, doc_length_A : float):
        """Initializes with file locations to be used for retrieval"""
        self.index_path = index_path
        self.vocab_path = vocab_path
        self.doc_length_A = doc_length_A

    def get_postings(self, term : str) -> Iterable[Posting]:
        """For a given term, retrieves the postings WITHOUT positions from disk"""
        postingsResult = []
        position = self.get_term_position(term)
        if position == -1:
            return postingsResult
        with open(self.index_path, "rb") as diskIndexFile:
            diskIndexFile.seek(position)
            dft = struct.unpack('i', diskIndexFile.read(4))[0]
            previousDocID = 0 # for gaps w/ doc IDs
            for i in range(dft): # loop through dft times (and gather each docs info)
                currentDocID = (struct.unpack('i', diskIndexFile.read(4))[0])+previousDocID
                previousDocID = currentDocID
                tftd = struct.unpack('i', diskIndexFile.read(4))[0]
                postingsResult.append(Posting(doc_id=currentDocID, tftd=tftd))
                diskIndexFile.seek(tftd*4, 1) # first arg: skip the positions for current doc, second arg: 1 means from current file position
        return postingsResult
        
    def get_postings_with_positions(self, term : str) -> Iterable[Posting]:
        """For a given term, retrieves the postings WITH positions from disk"""
        postingsResult = []
        position = self.get_term_position(term)
        if position == -1:
            return postingsResult
        with open(self.index_path, "rb") as diskIndexFile:
            diskIndexFile.seek(position)
            dft = struct.unpack('i', diskIndexFile.read(4))[0]
            previousDocID = 0 # for gaps w/ doc IDs
            for i in range(dft): # loop through dft times (and gather each docs info)
                currentDocID = (struct.unpack('i', diskIndexFile.read(4))[0])+previousDocID
                previousDocID = currentDocID
                tftd = struct.unpack('i', diskIndexFile.read(4))[0]
                previousPos = 0 # for gaps w/ positions
                positions = [] # add all at the end to the Posting
                for j in range(tftd): # loop through tftd times (and gather each position)
                    currentPos = (struct.unpack('i', diskIndexFile.read(4))[0])+previousPos
                    previousPos = currentPos
                    positions.append(currentPos)
                postingsResult.append(Posting(currentDocID, positions))
        return postingsResult

    def get_term_position(self, term : str):
        """Returns the terms position in the binary index on disk using the vocabulary db"""
        # should we keep the connection open with the db the entire runtime?
        connection = sqlite3.connect(self.vocab_path)
        cursor = connection.cursor()
        cursor.execute("SELECT byte FROM vocab WHERE term = ?", (term,))
        query_result = cursor.fetchone()
    
        if query_result:
            position = query_result[0]
        else:
            position = -1
        connection.close()
        return position

    def get_vocabulary(self) -> list[str]:
        pass
