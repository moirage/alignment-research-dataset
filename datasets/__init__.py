from pprint import pprint

from datasets.blogs import BLOG_REGISTRY
from datasets.ebooks import EBOOK_REGISTRY

DATASET_REGISTRY = {
    "blogs": BLOG_REGISTRY,
    "ebooks": EBOOK_REGISTRY,
}

ALL_DATASETS = sorted(list(DATASET_REGISTRY))


# TODO This pattern is duplicated in several __init__ files
def get_dataset(dataset_name):
    try:
        return DATASET_REGISTRY[dataset_name]
    except KeyError as e:
        print("Available datasets:")
        pprint(DATASET_REGISTRY)
        raise KeyError(f"Missing dataset {dataset_name}")
