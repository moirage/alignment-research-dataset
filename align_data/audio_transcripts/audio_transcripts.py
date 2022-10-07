from dataclasses import dataclass, field
import gdown
from align_data.common.alignment_dataset import AlignmentDataset , DataEntry
from typing import List
import zipfile
import os
import logging
import sys
import re

logging.basicConfig(format='%(asctime)s | %(levelname)s : %(message)s',
                    level=logging.INFO, stream=sys.stdout)
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

@dataclass
class AudioTranscripts(AlignmentDataset):

    otter_zip_url : str 
    transcript_path : str = "."

    def __post_init__(self):
        self.setup()
        if not os.path.exists(self.transcript_path):
            self._pull_from_gdrive()
        self.file_list = [xx for xx in os.listdir(os.path.join(self.transcript_path , 'transcripts')) if xx.endswith('.md')]


    def _pull_from_gdrive(self):
        logger.info("Pulling from gdrive")
        gdown.download(url=self.otter_zip_url, 
                       output=os.path.join(self.transcript_path, "transcripts.zip"), 
                       quiet=False)
        logger.info("Unzipping")
        with zipfile.ZipFile(os.path.join(self.transcript_path, "transcripts.zip"), 'r') as zip_ref:
            zip_ref.extractall(self.transcript_path)
            
            
    
    def fetch_entries(self):
        for ii, filename in enumerate(self.file_list):
            if self._entry_done(ii):
                logger.info(f"Already done {ii}")
                continue
            
            logger.info(f"Processing {filename}")
            text = open(os.path.join(self.transcript_path, 'transcripts', filename), "r").read()
            title = filename.split(".")[0]
            
            date = re.search(r"\d{4}\d{2}\d{2}", filename).group(0)
            date = date[:4] + "-" + date[4:6] + "-" + date[6:]
            
            new_entry = DataEntry({
                "source": "audio-transcripts",
                "source_filetype": "audio",
                "url": "n/a",
                "converted_with": "otter-ai",
                "title": title,
                "authors": "unknown",
                "date_published": str(date),
                "text": text,
            })
            new_entry.add_id()
            yield new_entry            
