import pprint
from querying.notquery import NotQuery
from querying.phraseliteral import PhraseLiteral
from text.intermediatetokenprocessor import IntermediateTokenProcessor

from text.tokenprocessor import TokenProcessor
from .querycomponent import QueryComponent
from indexing import Index, Posting

from querying import querycomponent 

class AndQuery(QueryComponent):
    def __init__(self, components : list[QueryComponent]):
        # please don't rename the "components" field.
        self.components = components

    def get_postings(self, index : Index, token_processor : TokenProcessor) -> list[Posting]:
        previousPostings = 0
        result = []
        for component in self.components:
            isPositive = True
            result = []
            if not component.is_positive():
                isPositive = False
                component = component.component
            if type(component) is PhraseLiteral:
                currentPostings = component.get_postings(index, token_processor)
            else:
                component.term = token_processor.process_token(component.term)
                if type(component.term) is list:
                    component.term = component.term[-1]
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
                    if isPositive:
                        result.append(previousPostings[pprevious])
                    pprevious += 1
                    pcurrent += 1
                elif previousDoc < currentDoc:
                    if not isPositive:
                        result.append(previousPostings[pprevious])
                    pprevious += 1
                else:
                    pcurrent += 1
            previousPostings = result

        return result

    def __str__(self):
        return " AND ".join(map(str, self.components))