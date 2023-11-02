class Posting:
    """A Posting encapulates a document ID associated with a search query component."""
    def __init__(self, doc_id : int, positions : list = None):
        self.doc_id = doc_id
        self.positions = positions
