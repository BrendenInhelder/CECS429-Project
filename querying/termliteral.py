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

    def get_postings(self, index, token_processor : TokenProcessor) -> list[Posting]:
        self.term = token_processor.process_token(self.term)[0] # Won't this break if it's using a BasicTokenProcessor because of the index?
        return index.get_postings(self.term)

    def __str__(self) -> str:
        return self.term