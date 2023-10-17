from .querycomponent import QueryComponent
from indexing import Index, Posting

class NotQuery(QueryComponent):
    def __init__(self, component : QueryComponent):
        self.component = component
    
    def is_positive(self) -> bool:
        return False
    
    def get_postings(self, index) -> list[Posting]:
        return self.component.get_postings(index)
    
    def __str__(self):
        return f"NOT ({str(self.component)})"