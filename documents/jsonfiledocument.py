import io
from pathlib import Path
from typing import Iterable
from .document import Document
import json

class JsonFileDocument(Document):
    """
    Represents a document that is saved as a json file in the local file system.
    """
    def __init__(self, id : int, path : Path):
        super().__init__(id)
        self.path = path

    @property
    def title(self) -> str:
        # TODO: return with name of document too
        # return self.path.stem
        with open(self.path, encoding='utf-8') as json_file:
            json_data = json.load(json_file)
            return json_data.get("title", "")
    
    @property
    def file_name(self) -> str:
        return (str(self.path.stem) + ".json")

    def get_content(self) -> Iterable[str]:
        with open(self.path, encoding='utf-8') as json_file:
            json_data = json.load(json_file)
            body_text = json_data.get("body", "")
            return io.StringIO(body_text)


    @staticmethod
    def load_from(abs_path : Path, doc_id : int) -> 'JsonFileDocument' :
        """A factory method to create a JsonFileDocument around the given file path."""
        return JsonFileDocument(doc_id, abs_path)