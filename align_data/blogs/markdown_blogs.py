from dataclasses import dataclass
import os
import re
import gdown
import json
# from align_data.common.utils import *
from align_data.common.alignment_dataset import AlignmentDataset, DataEntry
import zipfile
import logging
import sys

logging.basicConfig(format='%(asctime)s | %(levelname)s : %(message)s',
                    level=logging.INFO, stream=sys.stdout)
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

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
    
    gdrive_address : str
    markdown_path : str
    
    def __post_init__(self):
        self.setup()
        logger.info(f"Checking if scrape exist in path {self.markdown_path}")
        os.mkdir(self.markdown_path) if not os.path.exists(self.markdown_path) else None
        if not os.path.exists(os.path.join(self.markdown_path , f'{self.name}.zip')):
            logger.info("Downloading scrape")
            self.pull_from_gdrive()
        if os.path.exists(os.path.join(self.markdown_path , f'{self.name}-cleaned-up')):
            self.file_list = [xx for xx in os.listdir(os.path.join(self.markdown_path , f'{self.name}-cleaned-up')) if xx.endswith('.md')]
        else:
            self.file_list = [xx for xx in os.listdir(os.path.join(self.markdown_path , f'{self.name}')) if xx.endswith('.md')]

    def pull_from_gdrive(self):
        gdown.download(url=self.gdrive_address, output=os.path.join(self.markdown_path, f"{self.name}.zip"), quiet=False)
        
        logger.info("Unzipping")
        with zipfile.ZipFile(os.path.join(self.markdown_path, f"{self.name}.zip"), 'r') as zip_ref:
            zip_ref.extractall(self.markdown_path)
    
    def fetch_entries(self):
        for ii  ,filename in enumerate(self.file_list):
            if self._entry_done(ii):
                logger.info(f"Already done {ii} , {filename}")
                continue
            if os.path.exists(os.path.join(self.markdown_path , f'{self.name}-cleaned-up')):
                with open(os.path.join(self.markdown_path , f'{self.name}-cleaned-up'  ,filename) , "r") as f:
                    text = f.read()
            else:
                with open(os.path.join(self.markdown_path , f'{self.name}'  ,filename) , "r") as f:
                    text = f.read()
            try:
                title = re.search(r"^#\s(.*)\n$", text, re.MULTILINE).group(1)
                date = re.search(r"^\d{4}-\d{2}-\d{2}", text, re.MULTILINE).group(0)
            except:
                title , date = filename.split(".md")[0] , "n/a"
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

    # def fetch_entries(self):
    #     print(f"Fetching {self.name} entries")
    #     self.setup()
    #     self.folder_name = self.RAW_DIR + "/" + self.folder_name
    #     self.download_md()

    #     # create dictionary to store the entries
    #     self.num_entries = len(os.listdir(self.folder_name))
    #     for i, file in enumerate(os.listdir(self.folder_name)):
    #         file = os.path.join(self.folder_name, file)
    #         self.fetch_individual_entries(i, file)

    #     os.makedirs("data/processed/jsons/markdown_blogs", exist_ok=True)

    #     json.dump(
    #         self.entries,
    #         open(f"data/processed/jsons/markdown_blogs/{self.name}.json", "w"),
    #     )
    #     print(f"Finished updating {self.name}.json.")

    #     print(
    #         f"Converting {self.name}.json to {self.name}.jsonl and {self.name}.txt..."
    #     )
    #     for k in self.entries.keys():
    #         yield self.entries[k]

    # def fetch_individual_entries(self, i, file):
    #     print(f"Processing entry {i}/{self.num_entries}")

    #     # grab the title by opening the .md file and grabbing the text in between ## and \n
    #     with open(file, "r") as f:
    #         text = f.read()
    #     title = re.search(r"^#\s(.*)\n$", text, re.MULTILINE).group(1)
    #     date = re.search(r"^\d{4}-\d{2}-\d{2}", text, re.MULTILINE).group(0)

    #     self.entries[i] = {
    #         "source": self.name,
    #         "source_type": "markdown",
    #         "title": title,
    #         "authors": self.authors,
    #         "date_published": str(date),
    #         "text": text,
    #     }

    # def setup(self):
    #     self.PROJECT_DIR = os.getcwd()
    #     self.RAW_DIR = os.path.join(self.PROJECT_DIR, "data/raw/markdown_blogs")

    # def download_md(self):
    #     os.makedirs(self.RAW_DIR, exist_ok=True)
    #     os.chdir(self.RAW_DIR)
    #     print("Downloading everything...")
    #     self.pull_from_gdrive()
    #     # unzip the downloaded folder
    #     print("Unzipping...")
    #     os.system("unzip -o " + f"{self.name}.zip -d " + ".")
    #     # remove the zip files
    #     os.system("rm " + "*.zip")
    #     os.chdir(self.PROJECT_DIR)

