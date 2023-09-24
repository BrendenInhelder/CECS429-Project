from abc import ABC, abstractmethod
from indexing import Posting

class QueryComponent(ABC):
    """
    A QueryComponent is one piece of a larger query, whether that piece is a literal string or represents a merging of
    other components. All nodes in a query parse tree are QueryComponent objects.
    """

    @abstractmethod
    def get_postings(self, index) -> list[Posting]:
        """
        Retrieves a list of postings for the query component, using an Index as the source.
        """
        pass