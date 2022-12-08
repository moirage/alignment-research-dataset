from dataclasses import dataclass
import gdown
from align_data.common.alignment_dataset import AlignmentDataset, DataEntry
import logging
import zipfile
import grobid_tei_xml
from tqdm import tqdm

logger = logging.getLogger(__name__)

@dataclass
class Reports(AlignmentDataset):

    gdrive_url : str
    done_key = "filename"

    def setup(self):
        self._setup()

        self.local_out = self.write_jsonl_path.parent / 'raw'

        if not (self.local_out / "report_teis.zip").exists():
            logger.info("Downloading everything...")
            self.pull_from_gdrive()

        logger.info("Unzipping")
        with zipfile.ZipFile(self.local_out / "report_teis.zip", 'r') as zip_ref:
            zip_ref.extractall(self.local_out)

    def pull_from_gdrive(self):
        gdown.download(
            url=self.gdrive_url,
            output=self.local_out / "report_teis.zip",
            quiet=False,
        )

    def fetch_entries(self):
        self.setup()
        for ii, filename in enumerate(tqdm((self.local_out / "report_teis").files("*.xml"))):
            if self._entry_done(filename):
                # logger.info(f"Already done {filename}")
                continue

            logger.info(f"Processing {filename}")
            xml_text = open(filename, "r").read()
            try:
                doc_dict = grobid_tei_xml.parse_document_xml(xml_text).to_dict()

                logger.info(f"Doc: {list(doc_dict.keys())}")
                new_entry = DataEntry({
                    "source": self.name,
                    "source_filetype": "pdf",
                    "abstract": doc_dict["abstract"],
                    "authors": [xx["full_name"] for xx in doc_dict["header"]["authors"]],
                    "title": doc_dict["header"]["title"],
                    "text": doc_dict["body"],
                    "date_published": "n/a",
                    "url": "n/a",
                    "filename": filename,
                })
            except Exception as e:
                logger.error(f"Error: {e}")
                new_entry = DataEntry({
                    "source": self.name,
                    "source_filetype": "pdf",
                    "authors": "n/a",
                    "title": "n/a",
                    "text": "n/a",
                    "date_published": "n/a",
                    "url": "n/a",
                    "filename": filename,
                })
            
            new_entry.add_id()
            yield new_entry
