# %%
from dataclasses import dataclass
import pandas as pd
from align_data.common.alignment_dataset import AlignmentDataset , DataEntry
import logging
import sys
import jsonlines
import os

logging.basicConfig(format='%(asctime)s | %(levelname)s : %(message)s',
                    level=logging.INFO, stream=sys.stdout)
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
    
@dataclass
class AlignmentNewsletter(AlignmentDataset):
    
    newsletter_xlsx_path: str
    COOLDOWN: int = 1
    
    def __post_init__(self) -> None:
        self.setup()
        self.df = pd.read_excel(self.newsletter_xlsx_path)

    def fetch_entries(self):
        """
        For each row in the dataframe, create a new entry with the following fields: url, source,
        converted_with, source_type, venue, newsletter_category, highlight, newsletter_number,
        summarizer, opinion, prerequisites, read_more, title, authors, date_published, text
        """
        for ii , row in self.df.iterrows():
            if self._entry_done(ii):
                logger.info(f"Already done {ii}")
                continue
            new_entry = DataEntry({"url": "https://rohinshah.com/alignment-newsletter/",
                   "source": "alignment newsletter",
                   "converted_with": "python",
                   "source_type": "google-sheets",
                   "venue": str(row["Venue"]),  # arXiv, Distill, LessWrong, Alignment Forum, ICML 2018, etc
                   "newsletter_category": str(row["Category"]),
                   "highlight": True if row["Highlight?"] == "Highlight" else False,
                   "newsletter_number": str(row["Email"]),
                   "summarizer": str(row["Summarizer"]),
                   "opinion": str(row["My opinion"]),
                   "prerequisites": str(row["Prerequisites"]),
                   "read_more": str(row["Read more"]),
                   "title": str(row["Title"]),
                   "authors": str(row["Authors"]),
                   "date_published": row["Year"],
                   "text": str(row["Summary"]),
                   })
            new_entry.add_id()
            yield new_entry
            
 