import logging
import align_data.blogs as blogs
import align_data.ebooks as ebooks
import align_data.arxiv_papers as arxiv_papers
import align_data.nonarxiv_papers as nonarxiv_papers
import align_data.reports as reports
import align_data.greaterwrong as greaterwrong
import align_data.stampy as stampy
import align_data.audio_transcripts as audio_transcripts
import align_data.alignment_newsletter as alignment_newsletter
import align_data.distill as distill
from align_data import templates
from pprint import pprint


logger = logging.getLogger(__name__)


DATASET_REGISTRY = (
    blogs.BLOG_REGISTRY
    + ebooks.EBOOK_REGISTRY
    + arxiv_papers.ARXIV_REGISTRY
    + nonarxiv_papers.NONARXIV_PAPER_REGISTRY
    + reports.REPORT_REGISTRY
    + greaterwrong.GREATERWRONG_REGISTRY
    + stampy.STAMPY_REGISTRY
    + audio_transcripts.AUDIO_TRANSCRIPTS_REGISTRY
    + distill.DISTILL_REGISTRY
    + alignment_newsletter.ALIGNMENT_NEWSLETTER_REGISTRY
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
