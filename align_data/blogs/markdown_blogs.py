import os
import re
import gdown
import json
import jsonlines
from align_data.common.utils import *
from tqdm import tqdm


class MarkdownBlogs:
    def __init__(
        self,
        gdrive_address,
    ):
        self.name = "markdown_blogs"
        self.gdrive_address = gdrive_address

    """
    Fetches articles from a blog where the posts are stored in markdown files on Google Drive.
    This is useful for blogs where the author posts about alignment, but many other things as well.
    Either store them manually yourself or ask them to send you markdown files of the post and store them in Gdrive.
    Useful tip: MarkDownload is a browser extension that makes it easy to grab posts and clean them quickly.
    If there are only a few dozen posts, it may be worth it to take 15 minutes to curate the alignment posts
    and store the markdowns in Gdrive.
    """

    def fetch_entries(self):
        print("Fetching alignment_newsletter entries")
        self.setup()
        self.audio_transcripts = {}

        for json_file in os.listdir(self.local_out):
            yield json.load(open(os.path.join(self.local_out, json_file)))

        # delete the local files
        os.system("rm -rf " + self.local_teis)
        os.system("rm -rf " + self.local_out)
        os.chdir(self.PROJECT_DIR)

    def fetch_individual_entries(self, i):
        print(f"Processing entry {i}/{len(self.num_entries)}")

        self.audio_transcripts[i] = {
            "source": "audio_transcripts",
            "source_filetype": "audio",
            "audio_category": self.category,  # podcast, lecture, educational (Rob Miles),
            "converted_with": self.transcribed_with,
            "title": self.title,
            "authors": self.authors,
            "date_published": str(self.date),
            "url": self.url,
            "text": self.text,
        }

    def setup(self):
        self.PROJECT_DIR = os.getcwd()
        self.RAW_TRANSCRIPTS_DIR = os.path.join(
            self.PROJECT_DIR, "data/raw/audio_transcripts/"
        )
        sh(f"mkdir -p {self.PROJECT_DIR}/data/raw/audio_transcripts")
        if os.path.exists(f"{self.PROJECT_DIR}/data/audio_transcripts.jsonl"):
            os.remove(f"{self.PROJECT_DIR}/data/audio_transcripts.jsonl")
        if os.path.exists(f"{self.PROJECT_DIR}/data/audio_transcripts.txt"):
            os.remove(f"{self.PROJECT_DIR}/data/audio_transcripts.txt")
        self.download_transcripts()

    def download_transcripts(self):
        os.chdir(self.RAW_TRANSCRIPTS_DIR)
        print("Downloading everything...")
        self.pull_from_gdrive()
        self.pull_from_otter()
        # unzip the downloaded folder
        print("Unzipping...")
        os.system("unzip -o " + "transcripts.zip -d " + ".")
        # remove the zip files
        os.system("rm " + "*.zip")
        os.chdir(self.PROJECT_DIR)

    def pull_from_gdrive(self):
        gdown.download(url=self.gdrive_address, output="transcripts.zip", quiet=False)

    def pull_from_otter(self):
        os.system("wget -O " + "transcripts.zip " + self.gdrive_address)
