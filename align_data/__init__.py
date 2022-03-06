import align_data.blogs

DATASET_REGISTRY = blogs.BLOG_REGISTRY

ALL_DATASETS = sorted([dataset.name for dataset in DATASET_REGISTRY])
DATASET_MAP = dict([(dataset.name, dataset) for dataset in DATASET_REGISTRY])

def get_dataset(name):
    try:
        return DATASET_MAP[name]
    except KeyError as e:
        print("Available datasets:")
        pprint(ALL_DATASETS)
        raise KeyError(f"Missing dataset {name}")
