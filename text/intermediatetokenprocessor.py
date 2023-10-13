from .tokenprocessor import TokenProcessor
import re
import nltk
from nltk.stem import PorterStemmer

class IntermediateTokenProcessor(TokenProcessor):
    """An IntermediateTokenProcessor creates terms (as a list) from tokens by splitting on hyphens
    to create a list of tokens, removing all non-alphanumeric characters from the beginning or end of token
    and ' and " from anywhere in token, and converting it to all lowercase."""
    stemmer = PorterStemmer()
    
    def process_token(self, token : str) -> list:
        tokens = [token]
        # create individual tokens with '-' as separator, but also altogether without '-'
        if '-' in token:
            tokens = token.split('-')
            tokens.append(''.join(tokens))
        # remove all non-alphanumeric characters from beginning and end, but not in middle of token
        #   also remove ' and "
        #   also convert to lowercase
        for i in range(len(tokens)):
            newToken = re.sub(r'^[^a-zA-Z0-9]+|[^a-zA-Z0-9]+$', '', tokens[i])
            newToken = re.sub(r"'", "", newToken)
            newToken = re.sub(r'"', "", newToken)
            newToken = newToken.lower()
            newToken = self.normalize_type(newToken)
            tokens[i] = newToken
        return tokens
        
    def normalize_type(self, type : str) -> str:
        return self.stemmer.stem(type)