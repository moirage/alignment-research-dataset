import os
import re
import gdown
import requests
import json
import jsonlines
from align_data.common.utils import *
from tqdm import tqdm


class AudioTranscripts:
    def __init__(
        self,
        name,
        gdrive_address,
    ):
        self.name = name
        self.gdrive_address = gdrive_address

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
            "source": "audio-transcripts",
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
        os.system("wget -O " + "otter_transcripts.zip " + self.gdrive_address)
