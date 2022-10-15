import align_data.arbital as arbital
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
import align_data.gdocs as gdocs

DATASET_REGISTRY = (
    arbital.ARBITAL_REGISTRY
    + blogs.BLOG_REGISTRY
    + ebooks.EBOOK_REGISTRY
    + arxiv_papers.ARXIV_REGISTRY
    + nonarxiv_papers.NONARXIV_PAPER_REGISTRY
    + reports.REPORT_REGISTRY
    + greaterwrong.GREATERWRONG_REGISTRY
    + stampy.STAMPY_REGISTRY
    + audio_transcripts.AUDIO_TRANSCRIPTS_REGISTRY
    + distill.DISTILL_REGISTRY
    + alignment_newsletter.ALIGNMENT_NEWSLETTER_REGISTRY
    + gdocs.GDOCS_REGISTRY
)

ALL_DATASETS = sorted([dataset.name for dataset in DATASET_REGISTRY])
DATASET_MAP = dict([(dataset.name, dataset) for dataset in DATASET_REGISTRY])


def get_dataset(name):
    try:
        return DATASET_MAP[name]
    except KeyError as e:
        print("Available datasets:")
        print(ALL_DATASETS)
        raise KeyError(f"Missing dataset {name}")
