import abc
import typing


class Dataset(abc.ABC):
    """
    A Dataset is used to download/scrape and clean a single data source
    """

    @abc.abstractmethod
    def name(self) -> str:
        """
        The human-readable name of this dataset.
        """
        raise NotImplementedError

    @abc.abstractmethod
    def fetch_entries(self) -> typing.Iterable[dict]:
        """
        Generates data as a `Iterable[dict]` from downloaded resources.

        Each `dict` should adhere to the following attribute structure:
        {
            'content': The raw content of the entry (e.g., HTML).
            'text': The cleaned plain text of the entry.
            'metadata': A `dict` of various metadata fields specific to this dataset.
        }
        """
        raise NotImplementedError
