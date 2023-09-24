import pprint
from .querycomponent import QueryComponent
from indexing import Index, Posting

from querying import querycomponent 

class AndQuery(QueryComponent):
    def __init__(self, components : list[QueryComponent]):
        # please don't rename the "components" field.
        self.components = components

    def get_postings(self, index : Index) -> list[Posting]:
        previousSet = 0
        for component in self.components:
            postings = set((index.get_postings(component.term)).keys())
            if previousSet == 0:
                previousSet = postings
                continue
            previousSet = previousSet.intersection(postings)
        return list(previousSet)

    def __str__(self):
        return " AND ".join(map(str, self.components))