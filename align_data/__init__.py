import logging
import align_data.blogs as blogs
import align_data.ebooks as ebooks
import align_data.lesswrong as lesswrong
from align_data import templates
from pprint import pprint


logger = logging.getLogger(__name__)


DATASET_REGISTRY = (
    blogs.BLOG_REGISTRY + 
    ebooks.EBOOK_REGISTRY + 
    lesswrong.LESSWRONG_REGISTRY
)

ALL_DATASETS = sorted([dataset.name for dataset in DATASET_REGISTRY])
DATASET_MAP = dict([(dataset.name, dataset) for dataset in DATASET_REGISTRY])


def get_dataset(name: str) -> templates.Dataset:
    """ Returns a dataset by name. """
    try:
        return DATASET_MAP[name]
    except KeyError as missing_dataset_error:
        list_datasets()
        raise missing_dataset_error(f"Missing dataset {name}")


def list_datasets():
    """ Prints all the datasets in the registry. """
    print("Available datasets:")
    pprint(ALL_DATASETS)
