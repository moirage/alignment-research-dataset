from dataclasses import dataclass
import requests
import logging
from align_data.common.alignment_dataset import AlignmentDataset , DataEntry
from tqdm import tqdm

logger = logging.getLogger(__name__)

@dataclass
class Stampy(AlignmentDataset):

    index_url : str
    done_key = "entry"

    def setup(self):
        self._setup()

    def fetch_entries(self):
        self.setup()
        entries = dict(requests.get(self.index_url).json())
        for ii, entry in enumerate(tqdm(entries["results"].keys())):
            if self._entry_done(entry):
                # logger.info(f"Already done {entry}")
                continue
            qa_entry = entries["results"][entry]
            qa_entry["question"] = ' '.join(entry.split("to ")[1:])
            qa_entry["answer"] = entries["results"][entry]["printouts"]["Answer"]
            qa_entry["text"] = "Question: " + qa_entry["question"] + "\n\nAnswer: " + entries["results"][entry]["printouts"]["Answer"][0]
            # if there is more than one answer, add the rest
            for jj in range(1, len(entries["results"][entry]["printouts"]["Answer"])):
                qa_entry["text"] += f"\n\nAnswer {str(jj)}: " + entries["results"][entry]["printouts"]["Answer"][jj]


            logger.info(f"Processing {ii}")

            new_entry = DataEntry({
                "source" : self.name,
                "source_filetype": "text",
                "url": "n/a",
                "title": qa_entry["question"],
                "authors": "n/a",
                "date_published": "n/a",
                "text": qa_entry["text"],
                "question": qa_entry["question"],
                "answer": qa_entry["answer"],
                "entry": entry
            })
            logger.info(f"Processing {entry}")
            new_entry.add_id()

            yield new_entry