import math
from pathlib import Path
import pprint
import re
import struct
import heapq
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
        # TODO: somehow Euclidean distance is far off from desired
        eucDist = 0
        for term in docTermFreq:
            wdt = 1 + math.log10(docTermFreq[term])
            eucDist += (wdt ** 2)
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

def ranked_queries(dir : DirectoryCorpus, diskIndexPath : Path, vocabDBPath : Path):
    """performs ranked retrieval queries, TODO: implement ranked_retrieval"""
    # Build the index over this directory
    print("***************Indexing*****************")
    index = positional_inverted_index_corpus(dir)
    print("************Done Indexing***************")
    token_processor = IntermediateTokenProcessor()

    diw = DiskIndexWriter()
    diw.writeIndex(index, diskIndexPath, vocabDBPath)
    print("*******Done Writing Index to Disk*******")

    diskIndex = DiskPositionalIndex(diskIndexPath, vocabDBPath) # can change to just be index once it verifiably works

    retrievalOption = "-1"
    while (retrievalOption != "1" or retrievalOption != "2"):
        retrievalOption = input("Ranked (1) or Probabilistic (2) Retrieval? Exit (0): ")
        if retrievalOption == "0":
            return
        if retrievalOption != "1" or retrievalOption != "2":
            print("Invalid input. Try again...")

    query = input('Enter a bag of words you would like to search for(\'quit\' to exit): ')
    while query != 'quit':
        print("query:", query)
        result = ranked_retrieval(diskIndex, token_processor, query, dir)
        if len(result) == 0:
            print("No results")
        else:
            print("\nResults:")
            for tuple in result: # tuple : (score, doc_id)
                print(dir.get_document(tuple[1]).title, " (", dir.get_document(tuple[1]).file_name, ", ID ", dir.get_document(tuple[1]).id, ")", ") = ", tuple[0], sep="")

        query = input('Enter a term you would like to search for(\'quit\' to exit): ')

def probabilistic_retrieval(index : Index, token_processor : TokenProcessor, query : str, dir : DirectoryCorpus) -> list:
    return []
def ranked_retrieval(index : Index, token_processor : TokenProcessor, query : str, dir : DirectoryCorpus) -> list:
    # t: term, wqt: weight for term t, ln: natural log (some library method), dft: document freq for that term (len(list of postings))
    # wdt: weight for doc d for each term t, tftd: term t freq for that term t in doc d
    # A_d: accumulator for doc d, += wqt x wdt, priority queue: put A_d / L_d for each doc in this to get best ones
    N = len(dir) # for all nps, should be 36803
    accumulators = {} # {doc_id -> A_d}
    priority_queue = [] # (A_d/L_d, doc_id)
    query = query.split()
    for t in query:
        print("t before processing:", t)
        t = token_processor.process_token(t)[0]
        t_postings = index.get_postings(t)
        dft = len(t_postings)
        if dft == 0:
            continue
        wqt = math.log(1+(N/dft))
        print(dft, " postings for term \"", t, "\" with wQt = ", wqt, sep="")
        for d in t_postings:
            tftd = d.tftd
            wdt = 1 + math.log(tftd)
            print("wDt(", dir.get_document(d.doc_id).title, " (", dir.get_document(d.doc_id).file_name, ", ID ", dir.get_document(d.doc_id).id, ")", ") = ", wdt, sep="")
            A_d = 0
            if d.doc_id not in accumulators:
                A_d = wqt * wdt
                accumulators[d.doc_id] = A_d
            else:
                A_d = accumulators[d.doc_id]
                A_d += wqt * wdt
                accumulators[d.doc_id] = A_d
    with open("docWeights.bin", "rb") as doc_weights_file:
        for doc_id in accumulators:
            offset = doc_id * 8 # doubles are stored in this file, so id * 8 will be corresponding doc's L_d
            doc_weights_file.seek(offset)
            L_d = struct.unpack('d', doc_weights_file.read(8))[0]
            print("Ld(", dir.get_document(doc_id).title, " (", dir.get_document(doc_id).file_name, ", ID ", dir.get_document(doc_id).id, ")", ") = ", L_d, sep="")
            A_d = accumulators[doc_id]
            heapq.heappush(priority_queue, (A_d / L_d, doc_id))
    top_10 = heapq.nlargest(10, priority_queue)
    return top_10

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

    dir = menu()
    query_type = "-1"
    while query_type != "1" or query_type != "2":
        query_type = input("Boolean (1) or Ranked (2) Queries? Exit (0): ")
        if query_type == "1":
            boolean_queries(dir, diskIndexPath, vocabDBPath)
            break
        elif query_type == "2":
            ranked_queries(dir, diskIndexPath, vocabDBPath)
            break
        elif query_type == "0":
            break
        else:
            print("Invalid input. Try again...")
