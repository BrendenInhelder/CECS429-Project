from pydoc import doc
from typing import Iterable
from .postings import Posting
from .index import Index


class InvertedIndex(Index):
    """Implements an Index using an inverted index. Does not require knowing the full corpus
    vocabulary and number of documents prior to construction."""

    def __init__(self):
        """Constructs an empty inverted index"""
        self.vocabulary = set()
        self.index = {}

    def add_term(self, term : str, doc_id : int):
        """Adds a document id to the postings_lists of the correct term in the dictionary
           { shakespeare: postings_list[1, 3, 4, ...] }."""
        if term not in self.index:
            self.index[term] = [Posting(doc_id)]
        else:
            postings_list = self.index[term]
            if (postings_list[len(postings_list)-1]).doc_id == doc_id:
                return
            postings_list.append(Posting(doc_id))
            self.index[term] = postings_list

    def get_postings(self, term : str) -> Iterable[Posting]:
        """Returns a list of Postings for all documents that contain the given term."""
        if term not in self.index:
            return []
        return self.index[term]

    def get_vocabulary(self) -> list[str]:
        """Returns sorted list of vocab, inefficient because everytime someone wants vocab it will have to sort"""
        vocab = list(self.vocabulary)
        vocab.sort()
        return vocab
