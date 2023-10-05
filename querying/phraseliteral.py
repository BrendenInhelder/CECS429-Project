from indexing.index import Index
from indexing.postings import Posting
from .querycomponent import QueryComponent

class PhraseLiteral(QueryComponent):
    """
    Represents a phrase literal consisting of one or more terms that must occur in sequence.
    """

    def __init__(self, terms : list[QueryComponent]):
        self.literals = terms

    def get_postings(self, index) -> list[Posting]:
        previousPostings = 0
        docIDs = []
        sharedIndexes = [] # holds the postings for each term
        for component in self.literals:
            sharedIndexes.append(index.get_postings(component.term))
            docIDs = []
            currentPostings = list((index.get_postings(component.term)).keys())
            if previousPostings == 0:
                previousPostings = currentPostings
                continue
            pprevious = 0
            pcurrent = 0
            while(pprevious < len(previousPostings) and pcurrent < len(currentPostings)):
                previousDoc = previousPostings[pprevious]
                currentDoc = currentPostings[pcurrent]
                if previousDoc == currentDoc:
                    # AND is true
                    docIDs.append(previousDoc)
                    pprevious += 1
                    pcurrent += 1
                elif previousDoc < currentDoc:
                    pprevious += 1
                else:
                    pcurrent += 1
            previousPostings = docIDs
        if len(docIDs) == 0:
            return docIDs
        # time to perform the merge...yay
        result = []
        for docID in docIDs: # loop through each docID to check if it has a phrase
            currentDocPositions = []
            for termPositions in sharedIndexes: # look at each term's position index, check only the current docID
                currentDocPositions.append(termPositions[docID])
            if self.check_positions(currentDocPositions):
                result.append(docID)
        return result

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