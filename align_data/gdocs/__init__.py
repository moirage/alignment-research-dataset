from .gdocs import Gdocs

file_ids = ["1gZc-z8kc_rdbIuInw8lqoA8cas2IpDLJ"]

GDOCS_REGISTRY = [
    Gdocs(f"https://drive.google.com/uc?id={file_id}") for file_id in file_ids
]
