from querying.andquery import AndQuery
from .querycomponent import QueryComponent
from indexing import Index, Posting

from querying import querycomponent 

class OrQuery(QueryComponent):
    def __init__(self, components : list[QueryComponent]):
        self.components = components

    def get_postings(self, index : Index) -> list[Posting]:
        # TODO: need to do union without sets
        previousSet = 0 
        for component in self.components:
            if type(component) == AndQuery:
                postings = set(component.get_postings(index))
            else:
                postings = set((index.get_postings(component.term)).keys())
            if previousSet == 0:
                previousSet = postings
                continue
            previousSet = previousSet.union(postings)
        return list(previousSet)

    def __str__(self):
        return "(" + " OR ".join(map(str, self.components)) + ")"