import os
import re
import gdown
import json
from align_data.common.utils import *


class MDEBooks:
    def __init__(self, gdrive_address, name):
        self.name = name
        self.folder_name = name
        self.gdrive_address = gdrive_address
        self.entries = {}

    """
    
    """

    def fetch_entries(self):
        print(f"Fetching {self.name} entries")
        self.setup()
        self.folder_name = self.RAW_DIR + "/" + self.folder_name
        self.download_md()

        # create dictionary to store the entries
        self.num_entries = len(os.listdir(self.folder_name))
        for i, file in enumerate(os.listdir(self.folder_name)):
            if file.endswith(".md"):
                file = os.path.join(self.folder_name, file)
                self.fetch_individual_entries(i, file)

        os.makedirs("data/processed/jsons/mdebooks", exist_ok=True)

        json.dump(
            self.entries,
            open(f"data/processed/jsons/mdebooks/{self.name}.json", "w"),
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
        filename = file.split("/")[-1]
        title = re.search(r"(.*)-by", filename, re.MULTILINE).group(1)
        date = re.search(r"\d{4}-\d{2}-\d{2}", filename).group(0)
        authors = re.search(r"-by\s(.*)-date", filename).group(1)

        self.entries[i] = {
            "source": self.name,
            "source_type": "markdown",
            "title": title,
            "authors": authors,
            "date_published": str(date),
            "text": text,
        }

    def setup(self):
        self.PROJECT_DIR = os.getcwd()
        self.RAW_DIR = os.path.join(self.PROJECT_DIR, "data/raw/")

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
