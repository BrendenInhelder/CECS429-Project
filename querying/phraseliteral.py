from indexing.index import Index
from indexing.postings import Posting
from text.tokenprocessor import TokenProcessor
from .querycomponent import QueryComponent

class PhraseLiteral(QueryComponent):
    """
    Represents a phrase literal consisting of one or more terms that must occur in sequence.
    """

    def __init__(self, terms : list[QueryComponent]):
        self.literals = terms

    def get_postings(self, index, token_processor : TokenProcessor) -> list[Posting]:
        # TODO: might be able to speed this up
        previousPostings = 0
        docIDs = []
        sharedIndexes = [] # holds the postings for each term
        for component in self.literals:
            # TODO: Can maybe replace some with? -> component.get_postings(index, token_processor)
            component.term = token_processor.process_token(component.term)
            if type(component.term) is list:
                component.term = component.term[-1]

            docIDs = []
            docANDTerms = {}
            previousTermANDPostings = []
            currentPostings = index.get_postings(component.term)
            sharedIndexes.append(currentPostings) # should be adding a list of Postings for the term e.g. [Posting(doc_id,positions), ...]

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
                    previousTermANDPostings.append(previousPostings[pprevious])
                    docID = previousPostings[pprevious].doc_id
                    docIDs.append(docID)
                    if docID not in docANDTerms:
                        docANDTerms[docID] = [previousPostings[pprevious].positions, currentPostings[pcurrent].positions]
                    else:
                        docANDTerms[docID] = docANDTerms[docID].append(currentPostings[pcurrent].positions)
                    pprevious += 1
                    pcurrent += 1
                elif previousDoc < currentDoc:
                    pprevious += 1
                else:
                    pcurrent += 1
            previousPostings = previousTermANDPostings
        
        if len(docIDs) == 0:
            return docIDs
        
        # time to perform the merge...yay
        # TODO: might be able to speed this up
        result = []

        # attempt 2:
        
        for docID in docIDs:
            currentDocPositions = []
            # print(docID, docANDTerms[docID])
            currentDocPositions = docANDTerms[docID]
            if self.check_positions(currentDocPositions):
                result.append(Posting(docID, currentDocPositions))
        return result

        # attempt 1:
        # for resultPostings in docIDs: # loop through each docID to check if it has a phrase
        #     docID = resultPostings.doc_id
        #     currentDocPositions = []
        #     for postingList in sharedIndexes: # look at each term's posting list
        #         for posting in postingList: # look at each posting
        #             if posting.doc_id == docID:
        #                 currentDocPositions.append(posting.positions)
        #                 break
        #     if self.check_positions(currentDocPositions):
        #         result.append(Posting(docID, currentDocPositions))
        # return result


    def check_positions(self, currentDocPositions) -> bool:
        # method to check each list of positions between terms for a phrase
        k = 1
        for position in currentDocPositions[0]:
            found = False
            while k < (len(currentDocPositions)):
                if (position+k) in currentDocPositions[k]:
                    found = True
                    k += 1
                else:
                    found = False
                    break
            if found:
                return True
        return False

    def __str__(self) -> str:
        return '"' + " ".join(map(str, self.literals)) + '"'