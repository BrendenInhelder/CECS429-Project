from typing import Iterable
from .postings import Posting
from .index import Index

class PositionalInvertedIndex(Index):
    """Implements an Index using an inverted index. Does not require knowing the full corpus
    vocabulary and number of documents prior to construction."""

    def __init__(self):
        """Constructs an empty inverted index"""
        self.vocabulary = set()
        self.index = {} # {term1: [Posting(id1,[list of positions]), Posting(id2, [list of positions])],

    def add_term(self, term : str, doc_id : int, position : int):
        """Adds a document id to the dictionary of the correct term in the index 
            and updates to include the position"""
        # if we don't have the term yet
        if term not in self.index:
            self.index[term] = [Posting(doc_id, [position])]
            return
        if doc_id != self.index[term][-1].doc_id:
            self.index[term].append(Posting(doc_id, [position]))
        else:
            self.index[term][-1].positions.append(position)

    def get_postings(self, term : str) -> list[Posting]:
        """Returns a list of Postings for all documents that contain the given term."""
        # TODO: currently both are the same to allow in memory to still function...change this one to only return doc ids (w/out positions)
        if term not in self.index:
            return []
        return self.index[term]
    
    def get_postings_with_positions(self, term : str) -> list[Posting]:
        """Returns a list of Postings for all documents that contain the given term."""
        if term not in self.index:
            return []
        return self.index[term]

    def get_vocabulary(self) -> list[str]:
        """Returns sorted list of vocab, inefficient because everytime someone wants vocab it will have to sort"""
        vocab = list(self.vocabulary)
        vocab.sort()
        return vocab