from pathlib import Path
from documents import DocumentCorpus, DirectoryCorpus
from indexing import Index, InvertedIndex
from text import BasicTokenProcessor, englishtokenstream


def inverted_index_corpus(corpus: DocumentCorpus) -> Index:
    token_processor = BasicTokenProcessor()
    inverted_index = InvertedIndex()

    for doc in corpus:
        print(f"Found document {doc.title}")
        token_stream = englishtokenstream.EnglishTokenStream(doc.get_content())
        for token in token_stream:
            term = token_processor.process_token(token)
            inverted_index.add_term(term, doc.id)
            inverted_index.vocabulary.add(term)
    return inverted_index

if __name__ == "__main__":
    corpus_path = Path()
    d = DirectoryCorpus.load_text_directory(corpus_path, ".txt")
    # Build the index over this directory.
    index = inverted_index_corpus(d)

    # We aren't ready to use a full query parser;
    # for now, we'll only support single-term queries.

    query = input('Enter a term you would like to search for(\'quit\' to exit): ')

    while query != 'quit':
        postings = index.get_postings(query)
        if len(postings) == 0:
            print(query, 'Not Found')
        else:
            print('Found \'' + query + '\' in')
            for p in postings:
                print((d.get_document(p.doc_id)).title)
        query = input('Enter a term you would like to search for(\'quit\' to exit): ')

    # Uncomment if you want the vocabulary printed
    # print('Vocab:')
    # print(index.get_vocabulary())
