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
    doc_length_A = 0 # average num of tokens for any doc, useful for probabilistic retrieval
    doc_length_D = {} # num of tokens for each doc d (doc_id->doc_length_d)
    eucDistances = []
    for doc in corpus:
        docTermFreq = {}
        position = 0
        doc_length_d = 0 # num of tokens for doc d
        token_stream = englishtokenstream.EnglishTokenStream(doc.get_content())
        for token in token_stream:
            doc_length_d += 1
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
            wdt = 1 + math.log(docTermFreq[term])
            eucDist += (wdt ** 2)
        eucDist = math.sqrt(eucDist)
        eucDistances.append(eucDist)
        # update the average doc length, still need to average at end
        doc_length_A += doc_length_d
        doc_length_D[doc.id] = doc_length_d
    # storing all euclidian distances in binary file
    bin_format = 'd'
    with open("docWeights.bin", 'wb') as doc_weights_file:
        for eucDistance in eucDistances:
            packed_data = struct.pack(bin_format, eucDistance)
            doc_weights_file.write(packed_data)
    # final average of doc lengths for any doc
    doc_length_A = doc_length_A / len(corpus_dir)
    # save the doc lengths and average doc length to disk file docLengths.bin
    # TODO: fix path to be the folder of their choosing which also holds vocab and index on disk
    with open("docLengths.bin", "wb") as doc_lengths_file:
        for doc_id in doc_length_D:
            packed_data = struct.pack(bin_format, doc_length_D[doc_id])
            doc_lengths_file.write(packed_data)
        # write average to the end of the file
        packed_data = struct.pack(bin_format, doc_length_A)
        doc_lengths_file.write(packed_data)
    return positional_inverted_index

def corpus_path_menu():
    userChoice = input("What kind of files will you be indexing?\n\t1) .txt\n\t2) .json\n\tChoice: ")
    if userChoice == "1":
        corpus_path = get_corpus_path()
        corpus_dir = DirectoryCorpus.load_text_directory(corpus_path, ".txt")
        return corpus_dir
    elif userChoice == "2":
        corpus_path = get_corpus_path()
        corpus_dir = DirectoryCorpus.load_json_directory(corpus_path, ".json")
        return corpus_dir
    else:
        print("file type not supported, try again")
        corpus_path_menu()
    
def get_corpus_path() -> Path:
    userPath = input("Provide the path to index (Windows: use double backslashes or single forwardslashes): ")
    userPath = userPath.replace('"', '')
    corpus_path = Path(userPath)
    return corpus_path

def get_folder_path() -> Path:
    userPath = input("Provide the path to on-disk folder (Windows: use double backslashes or single forwardslashes): ")
    userPath = userPath.replace('"', '')
    folder_path = Path(userPath)
    return folder_path

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

def ranked_queries(dir : DirectoryCorpus, diskIndexPath : Path, vocabDBPath : Path, docWeightsPath : Path, docLengthsPath : Path):
    """performs ranked retrieval queries, TODO: implement ranked_retrieval"""
    # Build the index over this directory
    print("***************Indexing*****************")
    # index = positional_inverted_index_corpus(dir)
    print("************Done Indexing***************")
    token_processor = IntermediateTokenProcessor()

    # diw = DiskIndexWriter()
    # diw.writeIndex(index, diskIndexPath, vocabDBPath)
    print("*******Done Writing Index to Disk*******")

    diskIndex = DiskPositionalIndex(diskIndexPath, vocabDBPath) # can change to just be index once it verifiably works

    retrievalOption = "-1"
    while (retrievalOption != "1" and retrievalOption != "2"):
        retrievalOption = input("Ranked (1) or Probabilistic (2) Retrieval? Exit (0): ")
        if retrievalOption == "0":
            return
        if retrievalOption != "1" and retrievalOption != "2":
            print("Invalid input. Try again...")

    query = input('Enter a bag of words you would like to search for(\'quit\' to exit): ')
    while query != 'quit':
        print("query:", query)
        if retrievalOption == "1":
            result = ranked_retrieval(diskIndex, token_processor, query, dir, docWeightsPath)
        else:
            result = probabilistic_retrieval(diskIndex, token_processor, query, dir, docLengthsPath)
        if len(result) == 0:
            print("No results")
        else:
            print("\nResults:")
            for tuple in result: # tuple : (score, doc_id)
                print(dir.get_document(tuple[1]).title, " (", dir.get_document(tuple[1]).file_name, ", ID ", dir.get_document(tuple[1]).id, ")", ") = ", tuple[0], sep="")

        query = input('Enter a term you would like to search for(\'quit\' to exit): ')

def probabilistic_retrieval(index : Index, token_processor : TokenProcessor, query : str, dir : DirectoryCorpus, docLengthsPath : Path) -> list:
    print("**********Probabilistic Retrieval*********")
    # TODO: implement the OKAPI BM-25 algorithm to return the 10 most probable documents for a given query
    """The same as ranked retrieval but we have different computations for wdt, wqt, and L_d
    wqt = max[0.1, ln((N-dft+0.5)/(dft+0.5))]
    wdt = (2.2*tftd)/(1.2*(0.25+0.75*(doc_length_d/doc_length_A))+tftd)
    L_d = 1
    doc_length_d = # of tokens in doc d
    doc_length_A = average # of tokens in any doc"""
    N = len(dir)
    accumulators = {}
    priority_queue = []
    doc_length_A = -1
    # obtain average doc length
    # with open("docLengths.bin", "rb") as doc_lengths_file:
    with open(docLengthsPath, "rb") as doc_lengths_file:
        offset = len(dir) * 8 # doubles are stored in this file, so num of docs * 8 will be last element in file (average)
        doc_lengths_file.seek(offset)
        doc_length_A = struct.unpack('d', doc_lengths_file.read(8))[0]
    doc_length_d = 1
    query = query.split()
    for t in query:
        print("t before processing:", t)
        t = token_processor.process_token(t)[-1]
        t_postings = index.get_postings(t)
        dft = len(t_postings)
        if dft == 0:
            continue
        wqt = max(0.1, math.log((N-dft+0.5)/(dft+0.5)))
        print(dft, " postings for term \"", t, "\" with wQt = ", wqt, sep="")
        for d in t_postings:
            tftd = d.tftd
            # obtain current doc's length
            # with open("docLengths.bin", "rb") as doc_lengths_file:
            with open(docLengthsPath, "rb") as doc_lengths_file:
                offset = d.doc_id * 8 # doubles are stored in this file, so doc_id * 8 gets the current docs length
                doc_lengths_file.seek(offset)
                doc_length_d = struct.unpack('d', doc_lengths_file.read(8))[0]
            wdt = (2.2*tftd)/(1.2*(0.25+0.75*(doc_length_d/doc_length_A))+tftd)
            print("wDt(", dir.get_document(d.doc_id).title, " (", dir.get_document(d.doc_id).file_name, ", ID ", dir.get_document(d.doc_id).id, ")", ") = ", wdt, sep="")
            A_d = 0
            if d.doc_id not in accumulators:
                A_d = wqt * wdt
                accumulators[d.doc_id] = A_d
            else:
                A_d = accumulators[d.doc_id]
                A_d += wqt * wdt
                accumulators[d.doc_id] = A_d
    for doc_id in accumulators:
        # since L_d has been defined as 1 by professor...A_d remains as score
        A_d = accumulators[doc_id]
        heapq.heappush(priority_queue, (A_d, doc_id))
    top_10 = heapq.nlargest(10, priority_queue)
    return top_10

def ranked_retrieval(index : Index, token_processor : TokenProcessor, query : str, dir : DirectoryCorpus, docWeightsPath : Path) -> list:
    print("**********Basic Ranked Retrieval*********")
    # t: term, wqt: weight for term t, ln: natural log (some library method), dft: document freq for that term (len(list of postings))
    # wdt: weight for doc d for each term t, tftd: term t freq for that term t in doc d
    # A_d: accumulator for doc d, += wqt x wdt, priority queue: put A_d / L_d for each doc in this to get best ones
    N = len(dir) # for all nps, should be 36803
    accumulators = {} # {doc_id -> A_d}
    priority_queue = [] # (A_d/L_d, doc_id)
    query = query.split()
    for t in query:
        print("t before processing:", t)
        t = token_processor.process_token(t)[-1] # TODO: is using [0] a problem? This will not be compatible with hyphens in query...try -1
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
    # with open("docWeights.bin", "rb") as doc_weights_file:
    with open(docWeightsPath, "rb") as doc_weights_file:
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
    # path for corpus (all): "C:\\Users\\Brend\\CECS429_Project_Files\\all-nps-sites"
    # path for on-disk folder: "C:\\Users\\Brend\\CECS429_Project_Files"

    # default paths for all nps index and vocab
    #TODO: "calculate" these paths given the folder directory
    diskIndexPath = Path("C:\\Users\\Brend\\CECS429_Project_Files\\index_on_disk.bin")
    vocabDBPath = Path("C:\\Users\\Brend\\CECS429_Project_Files\\vocabulary.db")
    docWeightsPath = Path("C:\\Users\\Brend\\CECS429_Project_Files\\docWeights.bin")
    docLengthsPath = Path("C:\\Users\\Brend\\CECS429_Project_Files\\docLengths.bin")

    # paths for NPS10
    # diskIndexPath = Path("C:\\Users\\Brend\\OneDrive\\Documents\\new_binary_file.bin")
    # vocabDBPath = Path("C:\\Users\\Brend\\OneDrive\\Documents\\vocabulary.db")

    print("Welcome to my search engine!")
    corpus_dir = corpus_path_menu()
    folder_path = get_folder_path()
    # diskIndexPath = folder_path + "/"
    query_type = "-1"
    while query_type != "1" and query_type != "2":
        query_type = input("Boolean (1) or Ranked (2) Queries? Exit (0): ")
        if query_type == "1":
            boolean_queries(corpus_dir, diskIndexPath, vocabDBPath)
            break
        elif query_type == "2":
            ranked_queries(corpus_dir, diskIndexPath, vocabDBPath, docWeightsPath, docLengthsPath)
            break
        elif query_type == "0":
            break
        else:
            print("Invalid input. Try again...")
