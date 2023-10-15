from querying.andquery import AndQuery
from text.tokenprocessor import TokenProcessor
from .querycomponent import QueryComponent
from indexing import Index, Posting

from querying import querycomponent 

class OrQuery(QueryComponent):
    def __init__(self, components : list[QueryComponent]):
        self.components = components

    def get_postings(self, index : Index, token_processor : TokenProcessor) -> list[Posting]:
        previousPostings = 0
        result = []
        for component in self.components:
            result = []
            component.term = token_processor.process_token(component.term)
            if type(component.term) is list:
                component.term = component.term[-1]
            if type(component) == AndQuery:
                currentPostings = component.get_postings(index)
            else:
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
                    result.append(previousPostings[pprevious])
                    pprevious += 1
                else:
                    result.append(currentPostings[pcurrent])
                    pcurrent += 1            
            if pprevious < len(previousPostings):
                result.extend(previousPostings[pprevious:])
            elif pcurrent < len(currentPostings):
                result.extend(currentPostings[pcurrent:])
            previousPostings = result
        return result

    def __str__(self):
        return "(" + " OR ".join(map(str, self.components)) + ")"