import math
from pathlib import Path
import pprint
import re
import struct
from documents import DocumentCorpus, DirectoryCorpus
from indexing import DiskPositionalIndex, Index, PositionalInvertedIndex
from indexing.diskindexwriter import DiskIndexWriter
from indexing.postings import Posting
from text import BasicTokenProcessor, englishtokenstream, IntermediateTokenProcessor
from querying import BooleanQueryParser
from text.tokenprocessor import TokenProcessor

def positional_inverted_index_corpus(corpus: DocumentCorpus) -> Index:
    token_processor = IntermediateTokenProcessor()
    # token_processor = BasicTokenProcessor()
    positional_inverted_index = PositionalInvertedIndex()

    currentDocNum = 0
    eucDistances = []
    for doc in corpus:
        docTermFreq = {}
        position = 0
        token_stream = englishtokenstream.EnglishTokenStream(doc.get_content())
        for token in token_stream:
            terms = token_processor.process_token(token) 
            if type(terms) is not list:
                positional_inverted_index.add_term(terms, doc.id, position)
                positional_inverted_index.vocabulary.add(terms)
                if terms not in docTermFreq:
                    docTermFreq[terms] = 1
                else:
                    docTermFreq[terms] += 1
            else:
                for term in terms:
                    positional_inverted_index.add_term(term, doc.id, position)
                    positional_inverted_index.vocabulary.add(term)
                    if term not in docTermFreq:
                        docTermFreq[term] = 1
                    else:
                        docTermFreq[term] += 1
            position += 1
        # calculate Euclidian Distance for current doc
        eucDist = 0
        for term in docTermFreq:
            eucDist += (docTermFreq[term] ** 2)
        eucDist = math.sqrt(eucDist)
        eucDistances.append(eucDist)
    # storing all euclidian distances in binary file
    bin_format = 'd'
    with open("docWeights.bin", 'wb') as doc_weights_file:
        for eucDistance in eucDistances:
            packed_data = struct.pack(bin_format, eucDistance)
            doc_weights_file.write(packed_data)
    return positional_inverted_index

def menu():
    print("Welcome to my search engine!")
    userChoice = input("What kind of files will you be indexing?\n\t1) .txt\n\t2) .json\n\tChoice: ")
    if userChoice == "1":
        corpus_path = getFilePath()
        d = DirectoryCorpus.load_text_directory(corpus_path, ".txt")
        return d
    elif userChoice == "2":
        corpus_path = getFilePath()
        d = DirectoryCorpus.load_json_directory(corpus_path, ".json")
        return d
    else:
        print("file type not supported, try again")
        menu()
    
def getFilePath() -> Path:
    userPath = input("Provide the path to index (Windows: use double backslashes or single forwardslashes): ")
    userPath = userPath.replace('"', '')
    corpus_path = Path(userPath)
    return corpus_path

def boolean_queries(d : DirectoryCorpus, diskIndexPath : Path, vocabDBPath : Path):
    """performs boolean queries"""
    # Build the index over this directory
    print("***************Indexing*****************")
    index = positional_inverted_index_corpus(d)
    print("************Done Indexing***************")
    token_processor = IntermediateTokenProcessor()

    diw = DiskIndexWriter()
    diw.writeIndex(index, diskIndexPath, vocabDBPath)
    print("*******Done Writing Index to Disk*******")

    diskIndex = DiskPositionalIndex(diskIndexPath, vocabDBPath) # can change to just be index once it verifiably works

    query = input('Enter a boolean query you would like to search for(\'quit\' to exit): ')
    while query != 'quit':
        queryComponent = BooleanQueryParser.parse_query(query)
        print("query:", queryComponent)
        result = queryComponent.get_postings(diskIndex, token_processor)
        if len(result) == 0:
            print("No results")
        else:
            for posting in result:
                print("Title:", d.get_document(posting.doc_id).title)
            print("Postings length:", len(result))

        query = input('Enter a term you would like to search for(\'quit\' to exit): ')

def ranked_queries(d : DirectoryCorpus, diskIndexPath : Path, vocabDBPath : Path):
    """performs ranked retrieval queries, TODO: implement ranked_retrieval"""
    # Build the index over this directory
    print("***************Indexing*****************")
    index = positional_inverted_index_corpus(d)
    print("************Done Indexing***************")
    token_processor = IntermediateTokenProcessor()

    diw = DiskIndexWriter()
    diw.writeIndex(index, diskIndexPath, vocabDBPath)
    print("*******Done Writing Index to Disk*******")

    diskIndex = DiskPositionalIndex(diskIndexPath, vocabDBPath) # can change to just be index once it verifiably works

    query = input('Enter a bag of words you would like to search for(\'quit\' to exit): ')
    while query != 'quit':
        # queryComponent = BooleanQueryParser.parse_query(query)
        print("query:", query)
        # result = queryComponent.get_postings(diskIndex, token_processor)
        result = ranked_retrieval(diskIndex, token_processor, query)
        if len(result) == 0:
            print("No results")
        else:
            for posting in result:
                print("Title:", d.get_document(posting.doc_id).title)
            print("Postings length:", len(result))

        query = input('Enter a term you would like to search for(\'quit\' to exit): ')

def ranked_retrieval(index : Index, token_processor : TokenProcessor, query : str) -> list:
    """performs ranked retrieval given an index, token processor, and a query as a bag of words
    Pseudocode/plan:
    for each term t in the query:
        Calculate wqt, using the formula: wqt = ln(1 + N/dft)
        For each document d in t's postings list:
            Calculate wdt = 1 + ln(tftd)
            Acquire an accumulator A_d for document d
            Increase the accumulator by wqt x wdt
    for each accumulator A_d:
        divide A_d by L_d, which DiskPositionalIndex class should be able to read from docWeights.bin file.
        put the quotient into a priority queue
    Using the priority queue, return the top 10 documents and their scores."""
    # t: term, wqt: weight for term t, ln: natural log (some library method), dft: document freq for that term (len(list of postings))
    # wdt: weight for doc d for each term t, tftd: term t freq for that term t in doc d
    # A_d: accumulator for doc d, += wqt x wdt, priority queue: put A_d / L_d for each doc in this to get best ones
    N = 36803 # TODO: rough estimate, need exact (dynamically)
    query = query.split()
    for t in query:
        print("t:", t)
        t = token_processor.process_token(t)[0]
        t_postings = index.get_postings(t)
        dft = len(t_postings)
        wqt = math.log(1+(N/dft))
        print(dft, " postings for term \"", t, "\" with wqt = ", wqt, sep="")
    return []

if __name__ == "__main__":
    # Testing Purposes #
    # path for 10 nps(json): "C:\\Users\\Brend\\OneDrive\\Desktop\\NPS10"
    # path for 10 ch(txt): "C:\\Users\\Brend\\OneDrive\\Desktop\\MD10"
    # path for single nps(json): "C:\\Users\\Brend\\OneDrive\\Desktop\\NPSSingle"
    # path for all: "C:\\Users\\Brend\\Documents\\all-nps-sites"

    # default paths for all nps index and vocab
    # diskIndexPath = Path("C:\\Users\\Brend\\OneDrive\\Desktop\\429_Project_Data\\index_on_disk.bin")
    # vocabDBPath = Path("C:\\Users\\Brend\\OneDrive\\Desktop\\429_Project_Data\\vocabulary.db")

    # paths for NPS10
    diskIndexPath = Path("C:\\Users\\Brend\\OneDrive\\Documents\\new_binary_file.bin")
    vocabDBPath = Path("C:\\Users\\Brend\\OneDrive\\Documents\\vocabulary.db")

    d = menu()
    # boolean_queries(d, diskIndexPath, vocabDBPath)
    ranked_queries(d, diskIndexPath, vocabDBPath)

