class Posting:
    """A Posting encapulates a document ID associated with a search query component."""
    def __init__(self, doc_id : int):
        self.doc_id = doc_id
    def __init__(self, doc_id : int, positions : list):
        self.doc_id = doc_id
        self.positions = positions
