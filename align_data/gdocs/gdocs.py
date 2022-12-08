from dataclasses import dataclass
import gdown
from align_data.common.alignment_dataset import AlignmentDataset , DataEntry
import logging
import zipfile
import pypandoc
from path import Path
import os
import docx
from tqdm import tqdm

logger = logging.getLogger(__name__)

@dataclass
class Gdocs(AlignmentDataset):

    gdrive_address : str
    done_key = "docx_name"

    def setup(self):
        self._setup()
        self.local_path = self.write_jsonl_path.parent / "raw"
        self.pull_drom_gdrive()

        logger.info('Unzipping...')
        self.gdoc_files = self.write_jsonl_path.parent / "raw" / "gdocs"
        with zipfile.ZipFile(self.write_jsonl_path.parent / "raw" / f"{self.name}.zip", 'r') as zip_ref:
            zip_ref.extractall(self.gdoc_files)
        logger.info('Unzipping done')


        self.pandoc_check_path = Path(os.getcwd()) / "/pandoc/pandoc"

        if self.pandoc_check_path.exists():
            logger.info("Make sure pandoc is configured correctly.")
            os.environ.setdefault("PYPANDOC_PANDOC", self.pandoc_check_path)

    def pull_drom_gdrive(self):
        if not (self.local_path / 'gdocs.zip').exists():
            gdown.download(url=self.gdrive_address, output=self.local_path / f"{self.name}.zip", quiet=False)
        else:
            logger.info("Already downloaded")

    def fetch_entries(self):
        self.setup()
        for ii , docx_filename in enumerate(tqdm(self.gdoc_files.files('*.docx'))):
            if self._entry_done(docx_filename):
                # logger.info(f"Already done {docx_filename}")
                continue

            logger.info(f"Fetching {self.name} entry {docx_filename}")
            try:
                text = pypandoc.convert_file(
                    docx_filename, "plain", extra_args=['--wrap=none'])
            except Exception as e:
                logger.error(f"Error converting {docx_filename}")
                logger.error(e)
                text = "n/a"

            metadata = self._get_metadata(docx_filename)

            new_entry = DataEntry({
                "source": self.name,
                "source_filetype": "docx",
                "converted_with": "pandoc",
                "title": metadata.title,
                "authors": metadata.author,
                "date_published": metadata.created if metadata.created else "n/a",
                "text": text,
                "url": "n/a",
                "docx_name": docx_filename,
            })

            new_entry.add_id()
            yield new_entry

    def _get_metadata(self , docx_filename):
        doc = docx.Document(docx_filename)
        return doc.core_properties