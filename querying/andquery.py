import pprint
from .querycomponent import QueryComponent
from indexing import Index, Posting

from querying import querycomponent 

class AndQuery(QueryComponent):
    def __init__(self, components : list[QueryComponent]):
        # please don't rename the "components" field.
        self.components = components

    def get_postings(self, index : Index) -> list[Posting]:
        previousPostings = 0
        result = []
        for component in self.components:            
            result = []
            # currentPostings = list((index.get_postings(component.term)).keys())
            currentPostings = index.get_postings(component.term)
            if previousPostings == 0:
                previousPostings = currentPostings
                continue
            pprevious = 0
            pcurrent = 0
            while(pprevious < len(previousPostings) and pcurrent < len(currentPostings)):
                previousDoc = previousPostings[pprevious].doc_id
                currentDoc = currentPostings[pcurrent].doc_id
                if previousDoc == currentDoc:
                    # AND is true
                    result.append(previousPostings[pprevious])
                    pprevious += 1
                    pcurrent += 1
                elif previousDoc < currentDoc:
                    pprevious += 1
                else:
                    pcurrent += 1
            previousPostings = result

        return result

        # previousPostings = 0
        # result = []
        # for component in self.components:            
        #     result = []
        #     currentPostings = list((index.get_postings(component.term)).keys())
        #     if previousPostings == 0:
        #         previousPostings = currentPostings
        #         continue
        #     pprevious = 0
        #     pcurrent = 0
        #     while(pprevious < len(previousPostings) and pcurrent < len(currentPostings)):
        #         previousDoc = previousPostings[pprevious]
        #         currentDoc = currentPostings[pcurrent]
        #         if previousDoc == currentDoc:
        #             # AND is true
        #             result.append(previousDoc)
        #             pprevious += 1
        #             pcurrent += 1
        #         elif previousDoc < currentDoc:
        #             pprevious += 1
        #         else:
        #             pcurrent += 1
        #     previousPostings = result

        # return result

        # previousSet = 0
        # for component in self.components:
        #     postings = index.get_postings(component.term) # returns list of postings
        #     postingsSet = set()
        #     for posting in postings:
        #         postingsSet.add(posting.doc_id)
        #     # postings = set((index.get_postings(component.term)).keys())
        #     if previousSet == 0:
        #         previousSet = postingsSet
        #         continue
        #     previousSet = previousSet.intersection(postingsSet)
        # return list(previousSet)

    def __str__(self):
        return " AND ".join(map(str, self.components))