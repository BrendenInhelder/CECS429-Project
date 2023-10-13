import pprint
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
            result = []
            component.term = token_processor.process_token(component.term)[0] # Won't this break if it's using a BasicTokenProcessor because of the index?
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

    def __str__(self):
        return " AND ".join(map(str, self.components))