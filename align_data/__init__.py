import align_data.blogs
import align_data.ebooks
import align_data.arxiv_papers
import align_data.nonarxiv_papers
import align_data.reports
import align_data.lesswrong
import align_data.stampy
import align_data.audio_transcripts
import align_data.alignment_newsletter
import align_data.distill


DATASET_REGISTRY = (
    blogs.BLOG_REGISTRY
    + ebooks.EBOOK_REGISTRY
    + arxiv_papers.ARXIV_REGISTRY
    + nonarxiv_papers.NONARXIV_PAPER_REGISTRY
    + reports.REPORT_REGISTRY
    + lesswrong.LESSWRONG_REGISTRY
    + stampy.STAMPY_REGISTRY
    + audio_transcripts.AUDIO_TRANSCRIPTS_REGISTRY
    + distill.DISTILL_REGISTRY
)

ALL_DATASETS = sorted([dataset.name for dataset in DATASET_REGISTRY])
DATASET_MAP = dict([(dataset.name, dataset) for dataset in DATASET_REGISTRY])


def get_dataset(name):
    try:
        return DATASET_MAP[name]
    except KeyError as e:
        print("Available datasets:")
        pprint(ALL_DATASETS)
        raise KeyError(f"Missing dataset {name}")