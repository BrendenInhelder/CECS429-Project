from typing import Iterable
from .postings import Posting
from .index import Index
from pathlib import Path

class DiskPositionalIndex(Index):
    """Implements an Index using an inverted index that exists on Disk. 
    It Is constructed in a binary file and this class retrieves them."""

    def __init__(self, index_path : Path, vocab_path : Path):
        """Initializes with file locations to be used for retrieval"""
        self.index_path = index_path
        self.vocab_path = vocab_path

    def get_postings(self, term : str) -> Iterable[Posting]:
        """Retrieves a sequence from disk of Postings of documents that contain the given term."""
        pass

    def get_term_position(self):
        """Returns the terms position in the binary index on disk using the vocabulary db"""
        pass
    def get_vocabulary(self) -> list[str]:
        pass
