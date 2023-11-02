from indexing.postings import Posting
from text.intermediatetokenprocessor import IntermediateTokenProcessor
from text.tokenprocessor import TokenProcessor
from .querycomponent import QueryComponent

class TermLiteral(QueryComponent):
    """
    A TermLiteral represents a single term in a subquery.
    """

    def __init__(self, term : str):
        self.term = term

    def get_postings_with_positions(self, index, token_processor : TokenProcessor) -> list[Posting]:
        self.term = token_processor.process_token(self.term) # Won't this break if it's using a BasicTokenProcessor because of the index?
        if type(self.term) is list:
            self.term = self.term[-1]
        return index.get_postings_with_positions(self.term)
    
    def get_postings(self, index, token_processor : TokenProcessor) -> list[Posting]:
        # will call the index method for skpping positions (only for disk index)
        self.term = token_processor.process_token(self.term) # Won't this break if it's using a BasicTokenProcessor because of the index?
        if type(self.term) is list:
            self.term = self.term[-1]
        return index.get_postings(self.term)

    def __str__(self) -> str:
        return self.term