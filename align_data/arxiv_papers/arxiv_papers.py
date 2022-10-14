import arxiv
import requests
import logging
import time
import pandas as pd
from dataclasses import dataclass
from markdownify import markdownify

from align_data.common.alignment_dataset import AlignmentDataset, DataEntry

logger = logging.getLogger(__name__)


@dataclass
class ArxivPapers(AlignmentDataset):
    papers_csv_path: str
    COOLDOWN: int = 1
    done_ids = []

    def __post_init__(self) -> None:
        """
        Load arxiv ids
        """
        self.setup()
        self.df = pd.read_csv(self.papers_csv_path)
        self.df_arxiv = self.df[self.df["Url"].str.contains(
            "arxiv.org/abs") == True].drop_duplicates(subset="Url", keep="first")
        self.arxiv_ids = [xx.split('/abs/')[1] for xx in self.df_arxiv.Url]

    def _get_arxiv_metadata(self, paper_id) -> arxiv.Result:
        """
        Get metadata from arxiv
        """
        search = arxiv.Search(id_list=[paper_id], max_results=1)
        return next(search.results())

    def fetch_entries(self) -> None:
        """
        Fetch entries
            - Check if entry is already done
            - Get metadata from arxiv
            - Get markdown from arxiv-vanity
            - Strip markdown
            - Write to jsonl
        output:
            - jsonl file with entries
        """
        for ii, ids in enumerate(self.arxiv_ids):
            logger.info(f"Processing {ids}")
            if self._entry_done(ii):
                logger.info(f"Already done {ii}")
                continue

            markdown = self.process_id(ids)

            if markdown is None:
                continue

            paper = self._get_arxiv_metadata(ids)
            new_entry = DataEntry({"url": self._get_arxiv_link(ids),
                                   "source": "arxiv",
                                   "source_type": "html",
                                   "converted_with": "markdownify",
                                   "title": paper.title,
                                   "authors": [str(x) for x in paper.authors],
                                   "date_published": str(paper.published),
                                   "data_last_modified": str(paper.updated),
                                   "abstract": paper.summary.replace("\n", " "),
                                   "author_comment": paper.comment,
                                   "journal_ref": paper.journal_ref,
                                   "doi": paper.doi,
                                   "primary_category": paper.primary_category,
                                   "categories": paper.categories,
                                   "text": markdown,
                                   })
            new_entry.add_id()
            yield new_entry
            time.sleep(self.COOLDOWN)

    def _get_vanity_link(self, paper_id) -> str:
        """
        Get arxiv vanity link
        """
        return f"https://www.arxiv-vanity.com/papers/{paper_id}"

    def _get_arxiv_link(self, paper_id) -> str:
        """
        Get arxiv link
        """
        return f"https://arxiv.org/abs/{paper_id}"

    def _strip_markdown(self, markdown) -> str:
        """
        Strip markdown
        """
        s_markdown = markdown.split("don’t have to squint at a PDF")[1]
        return s_markdown.split("\nReferences\n")[0].replace("\n\n", "\n")

    def _is_dud(self, markdown) -> bool:
        """
        Check if markdown is a dud
        """
        if "Paper Not Renderable" in markdown:
            return True
        if "don’t have to squint at a PDF" not in markdown:
            return True
        return False

    def process_id(self, paper_id) -> str:
        """
        Process arxiv id
        """
        v_link = self._get_vanity_link(paper_id)
        logger.info(f"Fetching {v_link}")
        r = requests.get(v_link, timeout=5 * self.COOLDOWN)
        markdown = markdownify(r.content)
        if self._is_dud(markdown):
            return None

        mardown_excerpt = markdown.replace('\n', '')[:100]
        logger.info(f"Stripping markdown, {mardown_excerpt}")
        s_markdown = self._strip_markdown(markdown)
        return s_markdown
