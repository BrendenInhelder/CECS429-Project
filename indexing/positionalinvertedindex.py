from typing import Iterable
from .postings import Posting
from .index import Index


class PositionalInvertedIndex(Index):
    """Implements an Index using an inverted index. Does not require knowing the full corpus
    vocabulary and number of documents prior to construction."""

    def __init__(self):
        """Constructs an empty inverted index"""
        self.vocabulary = set()
        self.index = {} # {term1: {id1:[list of positions], id2:[list of positions]},
                        #  term2: {...}

    def add_term(self, term : str, doc_id : int, position : int):
        """Adds a document id to the dictionary of the correct term in the index 
            and updates to include the position"""
        # if we don't have the term yet
        if term not in self.index:
            self.index[term] = {doc_id : [position]}
        # if the term has not been found in the document yet
        elif doc_id not in self.index[term]:
            self.index[term][doc_id] = [position]
        # add the new position to the corresponding term and
        else:
            self.index[term][doc_id].append(position)

    def get_postings(self, term : str) -> dict:
        """Returns a list of Postings for all documents that contain the given term."""
        if term not in self.index:
            return {}
        return self.index[term]

    def get_vocabulary(self) -> list[str]:
        """Returns sorted list of vocab, inefficient because everytime someone wants vocab it will have to sort"""
        vocab = list(self.vocabulary)
        vocab.sort()
        return vocab
