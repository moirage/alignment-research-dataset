import abc


class Dataset(abc.ABC):
    """A Dataset is used to download/scrape and clean a single data source"""

    """ Human-readable name of the dataset """
    name: str

    @abc.abstractmethod
    def documents(self):
        """Generator which yields each document in the dataset. This can yield any type"""
        pass

    @abc.abstractmethod
    def clean_document(self, document):
        """Cleans a document from this dataset, or returns None if it should be discarded"""
        pass

    def cleaned_documents(self):
        """Generator which yields clean documents. Yields type string"""
        clean_generator = (self.clean_document(doc) for doc in self.documents())
        return (doc for doc in clean_generator if doc is not None)


    # TODO Are these useful to add from https://github.com/EleutherAI/the-pile
    # def size(self):
    #     """ Return an estimate of the dataset size. Implementations may use a faster, less accurate estimate. """
    #     size = sum((len(doc.encode('utf-8') for doc in tqdm(self.documents())))
    #     print('size', self.name(), size)
    #     return size
    #
    # def num_docs(self):
    #     """ Return an estimate of the number of documents in the dataset. Implementations may use a faster, less accurate estimate. """
    #     size = len(list(map(lambda x: None, tqdm(self.documents()))))
    #     print('docs', self.name(), size)
    #     return size
