from dataclasses import dataclass
import re
import gdown
from align_data.common.alignment_dataset import AlignmentDataset , DataEntry
import logging
import zipfile
from tqdm import tqdm

logger = logging.getLogger(__name__)

@dataclass
class MDEBooks(AlignmentDataset):

    gdrive_address : str
    done_key = "file_name"

    def setup(self):
        self._setup()
        self.pull_from_gdrive()

        logger.info("Unzipping")
        with zipfile.ZipFile(self.write_jsonl_path.parent / "raw" / f"{self.name}.zip", 'r') as zip_ref:
            zip_ref.extractall(self.write_jsonl_path.parent / "raw" / "md_ebooks")
        self.md_files = self.write_jsonl_path.parent / "raw" / "md_ebooks"
        logger.info("Unzipping done")

    def pull_from_gdrive(self):
        if not (self.write_jsonl_path.parent / "raw" / f"{self.name}.zip").exists():
            gdown.download(url=self.gdrive_address, output= self.write_jsonl_path.parent / "raw" / f"{self.name}.zip", quiet=False)
        else:
            logger.info("Already downloaded")


    def fetch_entries(self):
        self.setup()
        for ii , filename in enumerate(tqdm(self.md_files.files('*.md'))):
            if self._entry_done(filename):
                # logger.info(f"Already done {filename}")
                continue

            logger.info(f"Fetching {self.name} entry {filename}")
            with open(filename, 'r') as f:
                text = f.read()
            title = re.search(r"(.*)-by", filename.name, re.MULTILINE).group(1)
            date = re.search(r"\d{4}-\d{2}-\d{2}", filename.name).group(0)
            authors = re.search(r"-by\s(.*)-date", filename.name).group(1)
            
            new_entry = DataEntry({
                "source": self.name,
                "source_type": "markdown",
                "title": title,
                "authors": authors,
                "date_published": str(date),
                "text": text,
                "url": "n/a",
                "filename": filename
            })
            new_entry.add_id()
            yield new_entry
