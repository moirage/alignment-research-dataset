from dataclasses import dataclass
from collections import UserDict
import hashlib
import os
import logging
import jsonlines
from path import Path


INIT_DICT = {
    "source" : None,
    "id" : None,
    "text" : None,
    "date_published" : None,
    "title" : None,
    "url" : None,
}

TEXT_LEN = 1000

logger = logging.getLogger(__name__)

@dataclass
class AlignmentDataset:
    name : str
    done_ids = []
    done_key = None

    def _setup(self) -> None:

        self.write_jsonl_path = Path(os.path.join(os.path.abspath( os.path.dirname( __file__ ) ) , "../../data/" + self.name + ".jsonl"))
        
        if not os.path.exists(self.write_jsonl_path):
            logger.info(f"No previous data found at {self.write_jsonl_path}")
            return None
        
        with jsonlines.open(self.write_jsonl_path, mode='r') as reader:
            for ii , entry in enumerate(reader):
                if self.done_key and self.done_key not in entry:
                    continue
                # logger.info(f"Found {entry['title']} number {ii} in {self.write_jsonl_path}")
                self.done_ids.append((self.name , entry[self.done_key] if self.done_key else ii))
    
    def __str__(self) -> str:
        return f"{self.name} dataset will be written to {self.write_jsonl_path}"

    def _entry_done(self , entry):
        """
        Check if entry is already done
        """
        return (self.name , entry) in self.done_ids

    def fetch_entries(self):
        raise NotImplementedError

    def setup(self):
        raise NotImplementedError


class DataEntry(UserDict):
    def __init__(self , *args , **kwargs):
        super().__init__(*args , **kwargs)
        for k , v in INIT_DICT.items():
            if k not in self:
                self[k] = v
                
    def add_id(self):
        assert self["text"] is not None , "Entry is missing text"
        text_excerpt = self["text"][:TEXT_LEN].encode("utf-8")
        self["id"] = hashlib.md5(text_excerpt).hexdigest()
        
    def _verify_id(self):
        assert self["id"] is not None , "Entry is missing id"
        assert self["text"] is not None , "Entry is missing text"
        text_excerpt = self["text"][:TEXT_LEN].encode("utf-8")
        assert self["id"] == hashlib.md5(text_excerpt).hexdigest() , "Entry id does not match text"
                
    def toJSON(self):
        for k , _ in INIT_DICT.items():
            assert self[k] is not None , f"Entry is missing key {k}"
        self._verify_id()
        return dict(self.data)
