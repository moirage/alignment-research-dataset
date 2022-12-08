from dataclasses import dataclass
import re
import gdown
from align_data.common.alignment_dataset import AlignmentDataset, DataEntry
import zipfile
import logging
from tqdm import tqdm

logger = logging.getLogger(__name__)


@dataclass
class MarkdownBlogs(AlignmentDataset):

    """
    Fetches articles from a blog where the posts are stored in markdown files on Google Drive.
    This is useful for blogs where the author posts about alignment, but many other things as well.
    Either store them manually yourself or ask them to send you markdown files of the post and store them in Gdrive.
    Useful tip: MarkDownload is a browser extension that makes it easy to grab posts and clean them quickly.
    If there are only a few dozen posts, it may be worth it to take 15 minutes to curate the alignment posts
    and store the markdowns in Gdrive.
    """

    gdrive_address: str
    done_key = None

    def setup(self):
        self._setup()
        self.markdown_path = self.write_jsonl_path.parent / "raw"
        logger.info(f"Checking if scrape exist in path {self.markdown_path}")
        self.markdown_path.makedirs_p()

        if not (self.markdown_path / f'{self.name}.zip').exists():
            logger.info("Downloading scrape")
            self.pull_from_gdrive()

        self.cleaned_path = self.markdown_path / f'{self.name}-cleaned-up' if (self.markdown_path / f'{self.name}-cleaned-up').exists() else self.markdown_path / f'{self.name}'
        
        self.file_list = [xx for xx in self.cleaned_path.files('*.md')]

    def pull_from_gdrive(self):
        gdown.download(url=self.gdrive_address, output= self.markdown_path / f"{self.name}.zip" , quiet=False)

        logger.info("Unzipping")
        with zipfile.ZipFile(self.markdown_path / f"{self.name}.zip", 'r') as zip_ref:
            zip_ref.extractall(self.markdown_path)

    def fetch_entries(self):
        self.setup()
        for ii, filename in enumerate(tqdm(self.file_list)):
            if self._entry_done(ii):
                # logger.info(f"Already done {ii} , {filename}")
                continue
            with open(filename , "r") as f:
                text = f.read()

            try:
                title = re.search(r"^#\s(.*)\n$", text, re.MULTILINE).group(1)
                date = re.search(r"^\d{4}-\d{2}-\d{2}",
                                 text, re.MULTILINE).group(0)
            except:
                title, date = filename.split(".md")[0], "n/a"

            new_entry = DataEntry({
                "source": self.name,
                "source_type": "markdown",
                "title": title,
                "authors": "n/a",
                "date_published": str(date),
                "text": text,
                "url": "n/a",
            })

            new_entry.add_id()
            yield new_entry