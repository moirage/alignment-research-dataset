from .arxiv_papers import ArxivPapers
import os

ARXIV_REGISTRY = [
    ArxivPapers(
        name = "arxiv_papers",
        papers_csv_path = os.path.join(os.path.abspath( os.path.dirname( __file__ ) ) , "../../tables/ai-alignment-papers.csv")),
]