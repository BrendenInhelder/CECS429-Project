from pathlib import Path
from documents import DocumentCorpus, DirectoryCorpus
from indexing import Index, TermDocumentIndex
from text import BasicTokenProcessor, englishtokenstream

"""This basic program builds a term-document matrix over the .txt files in 
the same directory as this file."""

def index_corpus(corpus : DocumentCorpus) -> Index:
    
    token_processor = BasicTokenProcessor()
    vocabulary = set()
    
    for doc in corpus:
        print(f"Found document {doc.title}")
        # TODO:
        #   Tokenize the document's content by creating an EnglishTokenStream around the document's .content()
        #   Iterate through the token stream, processing each with token_processor's process_token method.
        #   Add the processed token (a "term") to the vocabulary set.
        token_stream = englishtokenstream.EnglishTokenStream(doc.get_content())
        for token in token_stream:
            term = token_processor.process_token(token)
            vocabulary.add(term)

    # TODO:
    # After the above, next:
    # Create a TermDocumentIndex object, with the vocabular you found, and the len() of the corpus.
    # Iterate through the documents in the corpus:
    #   Tokenize each document's content, again.
    #   Process each token.
    #   Add each processed term to the index with .add_term().
    term_doc_index = TermDocumentIndex(vocabulary, len(corpus))

    for doc in corpus:
        token_stream = englishtokenstream.EnglishTokenStream(doc.get_content())
        for token in token_stream:
            term = token_processor.process_token(token)
            term_doc_index.add_term(term, doc.id)
    return term_doc_index

if __name__ == "__main__":
    corpus_path = Path()
    d = DirectoryCorpus.load_text_directory(corpus_path, ".txt")
    # Build the index over this directory.
    index = index_corpus(d)

    # We aren't ready to use a full query parser;
    # for now, we'll only support single-term queries.

    query = input('Enter a term you would like to search for(\'quit\' to exit): ')
    #query = "whale" # hard-coded search for "whale"
    while(query != 'quit'):
        postings = index.get_postings(query)
        if len(postings) == 0:
            print(query, 'Not Found')
        else:
            #print('Found', query, 'in:')
            print('Found \'' + query + '\' in')
            for p in postings:
                # print(f"Document ID {p.doc_id}")
                print((d.get_document(p.doc_id)).title)
        query = input('Enter a term you would like to search for(\'quit\' to exit): ')
    # TODO: fix this application so the user is asked for a term to search.
