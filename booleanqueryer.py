from pathlib import Path
import pprint
from documents import DocumentCorpus, DirectoryCorpus
from indexing import Index, PositionalInvertedIndex
from indexing.postings import Posting
from text import BasicTokenProcessor, englishtokenstream
from querying import BooleanQueryParser


def positional_inverted_index_corpus(corpus: DocumentCorpus) -> Index:
    token_processor = BasicTokenProcessor()
    positional_inverted_index = PositionalInvertedIndex()

    for doc in corpus:
        position = 0
        print(f"Found document {doc.title}")
        token_stream = englishtokenstream.EnglishTokenStream(doc.get_content())
        for token in token_stream:
            term = token_processor.process_token(token) 
            positional_inverted_index.add_term(term, doc.id, position)
            positional_inverted_index.vocabulary.add(term)
            position += 1
    return positional_inverted_index

if __name__ == "__main__":
    # TODO: user input for path, hard-coded for debugging purposes
    # corpus_path = Path() 
    # corpus_path = Path(r'C:\Users\Brend\OneDrive\Desktop\NPS10')
    corpus_path = Path(r'C:\Users\Brend\Documents\all-nps-sites')
    


    # can use either txt or json...TODO: possibly try PDFs?
    # d = DirectoryCorpus.load_text_directory(corpus_path, ".txt")
    d = DirectoryCorpus.load_json_directory(corpus_path, ".json")

    # Build the index over this directory.
    index = positional_inverted_index_corpus(d)

    query = input('Enter a term you would like to search for(\'quit\' to exit): ')
    # TODO: apply same tokenization/normalization to query terms?

    while query != 'quit':
        queryComponent = BooleanQueryParser.parse_query(query)
        print("query:", queryComponent)
        result = queryComponent.get_postings(index)
        print("result: ")
        for docID in result:
            print("Title:", (d.get_document(Posting(docID).doc_id)).title, "ID:", docID)
        query = input('Enter a term you would like to search for(\'quit\' to exit): ')

    # Uncomment if you want the vocabulary printed
    # print('Vocab:')
    # print(index.get_vocabulary())
