import requests
import logging

import pandas as pd

from align_data.common.alignment_dataset import AlignmentDataset , DataEntry
from tqdm import tqdm
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class Stampy(AlignmentDataset):

    done_key = None

    def setup(self):
        self._setup()
        self.DISTILL_POSTS_DIR = self.write_jsonl_path.parent / "raw" / "stampy" / "stampy.csv"
        self.df = pd.read_csv(self.DISTILL_POSTS_DIR)
        logger.info(f"Found {len(self.df)} entries in {self.DISTILL_POSTS_DIR}")

    def fetch_entries(self):
        self.setup()
        for ii, row in tqdm(self.df.iterrows()):
            if self._entry_done(ii):
                # logger.info(f"Already done {entry}")
                continue
            
            logger.info(f"Processing {ii}")

            new_entry = DataEntry({
                "source" : self.name,
                "source_filetype": "text",
                "url": row["Link"],
                "title": row["Question"],
                "authors": "n/a",
                "date_published": row["Doc Last Edited"],
                "text": row["Rich Text"],
            })
            new_entry.add_id()

            yield new_entry