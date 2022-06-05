import os
import re
import gdown
import json
from align_data.common.utils import *


class MarkdownBlogs:
    def __init__(
        self,
        gdrive_address,
        blog_name,
        gdown_folder_name,
        authors=None,
    ):
        self.name = blog_name
        self.gdrive_address = gdrive_address
        self.folder_name = gdown_folder_name
        self.authors = ""
        self.entries = {}

    """
    Fetches articles from a blog where the posts are stored in markdown files on Google Drive.
    This is useful for blogs where the author posts about alignment, but many other things as well.
    Either store them manually yourself or ask them to send you markdown files of the post and store them in Gdrive.
    Useful tip: MarkDownload is a browser extension that makes it easy to grab posts and clean them quickly.
    If there are only a few dozen posts, it may be worth it to take 15 minutes to curate the alignment posts
    and store the markdowns in Gdrive.
    """

    def fetch_entries(self):
        print(f"Fetching {self.name} entries")
        self.setup()
        self.folder_name = self.RAW_DIR + "/" + self.folder_name
        self.download_md()

        # create dictionary to store the entries
        self.num_entries = len(os.listdir(self.folder_name))
        for i, file in enumerate(os.listdir(self.folder_name)):
            file = os.path.join(self.folder_name, file)
            self.fetch_individual_entries(i, file)

        os.makedirs("data/processed/jsons/markdown_blogs", exist_ok=True)

        json.dump(
            self.entries,
            open(f"data/processed/jsons/markdown_blogs/{self.name}.json", "w"),
        )
        print(f"Finished updating {self.name}.json.")

        print(
            f"Converting {self.name}.json to {self.name}.jsonl and {self.name}.txt..."
        )
        for k in self.entries.keys():
            yield self.entries[k]

    def fetch_individual_entries(self, i, file):
        print(f"Processing entry {i}/{self.num_entries}")

        # grab the title by opening the .md file and grabbing the text in between ## and \n
        with open(file, "r") as f:
            text = f.read()
        title = re.search(r"^#\s(.*)\n$", text, re.MULTILINE).group(1)
        date = re.search(r"^\d{4}-\d{2}-\d{2}", text, re.MULTILINE).group(0)

        self.entries[i] = {
            "source": self.name,
            "source_type": "markdown",
            "title": title,
            "authors": self.authors,
            "date_published": str(date),
            "text": text,
        }

    def setup(self):
        self.PROJECT_DIR = os.getcwd()
        self.RAW_DIR = os.path.join(self.PROJECT_DIR, "data/raw/markdown_blogs")

    def download_md(self):
        os.makedirs(self.RAW_DIR, exist_ok=True)
        os.chdir(self.RAW_DIR)
        print("Downloading everything...")
        self.pull_from_gdrive()
        # unzip the downloaded folder
        print("Unzipping...")
        os.system("unzip -o " + f"{self.name}.zip -d " + ".")
        # remove the zip files
        os.system("rm " + "*.zip")
        os.chdir(self.PROJECT_DIR)

    def pull_from_gdrive(self):
        gdown.download(url=self.gdrive_address, output=f"{self.name}.zip", quiet=False)
