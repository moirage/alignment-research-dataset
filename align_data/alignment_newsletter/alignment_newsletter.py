# %%
import logging
import jsonlines

import pandas as pd

from dataclasses import dataclass
from align_data.common.alignment_dataset import AlignmentDataset , DataEntry
from tqdm import tqdm

logger = logging.getLogger(__name__)
    
@dataclass
class AlignmentNewsletter(AlignmentDataset):
    
    COOLDOWN: int = 1
    done_key = "title"
    
    def setup(self) -> None:
        self._setup()
        self.newsletter_xlsx_path = self.write_jsonl_path.parent / "raw" / "alignment_newsletter.xlsx"
        self.df = pd.read_excel(self.newsletter_xlsx_path)

    def fetch_entries(self):
        """
        For each row in the dataframe, create a new entry with the following fields: url, source,
        converted_with, source_type, venue, newsletter_category, highlight, newsletter_number,
        summarizer, opinion, prerequisites, read_more, title, authors, date_published, text
        """
        self.setup()
        for ii , row in tqdm(self.df.iterrows()):
            if self._entry_done(row['Title']):
                # logger.info(f"Already done {row['Title']}")
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
            
 