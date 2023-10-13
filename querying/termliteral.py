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
        self.term = token_processor.process_token(self.term)[0]
        # TODO: call normalize_type in process_token so we don't have to check
        if type(token_processor) is IntermediateTokenProcessor:
            self.term = token_processor.normalize_type(self.term)
        return index.get_postings(self.term)

    def __str__(self) -> str:
        return self.term