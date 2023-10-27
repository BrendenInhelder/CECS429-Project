from pathlib import Path
import pprint
import re
from documents import DocumentCorpus, DirectoryCorpus
from indexing import Index, PositionalInvertedIndex
from indexing.diskindexwriter import DiskIndexWriter
from indexing.postings import Posting
from text import BasicTokenProcessor, englishtokenstream, IntermediateTokenProcessor
from querying import BooleanQueryParser

# Testing Purposes #
# path for 10 nps(json): "C:\\Users\\Brend\\OneDrive\\Desktop\\NPS10"
# path for 10 ch(txt): "C:\\Users\\Brend\\OneDrive\\Desktop\\MD10"
# path for single nps(json): "C:\\Users\\Brend\\OneDrive\\Desktop\\NPSSingle"
# path for all: "C:\\Users\\Brend\\Documents\\all-nps-sites"

def positional_inverted_index_corpus(corpus: DocumentCorpus) -> Index:
    token_processor = IntermediateTokenProcessor()
    # token_processor = BasicTokenProcessor()
    positional_inverted_index = PositionalInvertedIndex()

    currentDocNum = 0
    for doc in corpus:
        position = 0
        print(currentDocNum)
        currentDocNum+=1
        # print(f"Found document {doc.title}")
        token_stream = englishtokenstream.EnglishTokenStream(doc.get_content())
        for token in token_stream:
            term = token_processor.process_token(token) 
            if type(term) is not list:
                positional_inverted_index.add_term(term, doc.id, position)
                positional_inverted_index.vocabulary.add(term)
            else:
                for terms in term:
                    positional_inverted_index.add_term(terms, doc.id, position)
                    positional_inverted_index.vocabulary.add(terms)
            position += 1
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

if __name__ == "__main__":

    d = menu()

    # Build the index over this directory
    index = positional_inverted_index_corpus(d)
    token_processor = IntermediateTokenProcessor()
    #token_processor = BasicTokenProcessor()

    diskIndexPath = "C:\\Users\\Brend\\OneDrive\\Documents\\new_binary_file.bin"
    diw = DiskIndexWriter()
    diw.writeIndex(index, diskIndexPath)
    # diw.readIndex(diskIndexPath)

    query = input('Enter a term you would like to search for(\'quit\' to exit): ')
    while query != 'quit':
        queryComponent = BooleanQueryParser.parse_query(query)
        print("query:", queryComponent)
        result = queryComponent.get_postings(index, token_processor)
        if len(result) == 0:
            print("No results")
        else:
            for posting in result:
                print("Title:", d.get_document(posting.doc_id).title)
            print("Postings length:", len(result))

        query = input('Enter a term you would like to search for(\'quit\' to exit): ')
    
    # Uncomment if you want the vocabulary printed
    # print('Vocab:')
    # print(index.get_vocabulary())
