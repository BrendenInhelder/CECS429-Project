import struct
from typing import Iterable
from .postings import Posting
from .index import Index
from pathlib import Path
import sqlite3

class DiskPositionalIndex(Index):
    """Implements an Index using an inverted index that exists on Disk. 
    It Is constructed in a binary file and this class retrieves them."""

    def __init__(self, index_path : Path, vocab_path : Path):
        """Initializes with file locations to be used for retrieval"""
        self.index_path = index_path
        self.vocab_path = vocab_path

    def get_postings(self, term : str) -> Iterable[Posting]:
        """Retrieves a sequence from disk of Postings of documents that contain the given term."""
        # TODO: only retrieves doc frequency as a proof of concept
        position = self.get_term_position("park")
        # print("position:", position)
        with open(self.index_path, "rb") as diskIndexFile:
            diskIndexFile.seek(position)
            packed_data = diskIndexFile.read(4)
            unpacked_data = struct.unpack('i', packed_data)
            print("doc frequency for term:", unpacked_data[0])
        pass

    def get_term_position(self, term : str):
        """Returns the terms position in the binary index on disk using the vocabulary db"""
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
