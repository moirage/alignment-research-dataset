import abc
from abc import abstractmethod

class Dataset(abc.ABC):
    @abstractmethod
    def fetch_entries(self):
        """
        Returns fetched entries as Iterable[dict].
        
        Each entry is a dict with the following keys:
            - "content": raw content of the entry (e.g., HTML)
            - "text": cleaned plain text of the entry
            - metadata keys: various metadata fields specific to the dataset
        """
        pass
