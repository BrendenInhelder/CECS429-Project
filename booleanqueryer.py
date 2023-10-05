from pathlib import Path
import pprint
from documents import DocumentCorpus, DirectoryCorpus
from indexing import Index, PositionalInvertedIndex
from indexing.postings import Posting
from text import BasicTokenProcessor, englishtokenstream, IntermediateTokenProcessor
from querying import BooleanQueryParser


def positional_inverted_index_corpus(corpus: DocumentCorpus) -> Index:
    token_processor = IntermediateTokenProcessor()
    # token_processor = BasicTokenProcessor()
    positional_inverted_index = PositionalInvertedIndex()

    for doc in corpus:
        position = 0
        print(f"Found document {doc.title}")
        token_stream = englishtokenstream.EnglishTokenStream(doc.get_content())
        for token in token_stream:
            term = token_processor.process_token(token) 
            if type(term) is not list:
                # term = token_processor.normalize_type(term)
                positional_inverted_index.add_term(term, doc.id, position)
                positional_inverted_index.vocabulary.add(term)
                position += 1
            else:
                for terms in term:
                    # terms = token_processor.normalize_type(terms)
                    positional_inverted_index.add_term(terms, doc.id, position)
                    positional_inverted_index.vocabulary.add(terms)
                    #TODO: how do we deal with positions of terms that technically don't exist because we created them from hyphens???
                    position += 1
    return positional_inverted_index

def get_query() -> str:
    #BUG: results in porter stemmer on more than one term because query not separated
    phraseQuery = False
    query = input('Enter a term you would like to search for(\'quit\' to exit): ')
    if query == 'quit':
        return query
    if query[0] == '\"'and query[-1] == '\"':
        phraseQuery = True
    token_processor = IntermediateTokenProcessor()
    query = token_processor.process_token(query)
    print("query as a list:", query)
    if type(query) is list:
        # not sure how to handle this yet...what if the user searches "co-education"? Do we search for all 3? (probably)
        query = query[0]
    print("query pre normal:", query)
    query = token_processor.normalize_type(query)
    if phraseQuery: # we need to retain the quotes for the boolean query parser to recognize as phrase query
        query = '\"' + query + '\"'
        phraseQuery = False
    return query

if __name__ == "__main__":
    # TODO: user input for path, hard-coded for debugging purposes
    # corpus_path = Path() 
    corpus_path = Path(r'C:\Users\Brend\OneDrive\Desktop\NPS10')
    # corpus_path = Path(r'C:\Users\Brend\Documents\all-nps-sites')

    # can use either txt or json...TODO: possibly try PDFs?
    # d = DirectoryCorpus.load_text_directory(corpus_path, ".txt")
    d = DirectoryCorpus.load_json_directory(corpus_path, ".json")

    # Build the index over this directory.
    index = positional_inverted_index_corpus(d)

    query = input('Enter a term you would like to search for(\'quit\' to exit): ')
    while query != 'quit':
        queryComponent = BooleanQueryParser.parse_query(query)
        print("query:", queryComponent)
        result = queryComponent.get_postings(index)
        if len(result) == 0:
            print("No results")
        else:
            print("result: ")
            for docID in result:
                # print(result) if you want to see the positions
                print("Title:", (d.get_document(Posting(docID).doc_id)).title, "ID:", docID)
        query = input('Enter a term you would like to search for(\'quit\' to exit): ')
    
    # Uncomment if you want the vocabulary printed
    # print('Vocab:')
    # print(index.get_vocabulary())
