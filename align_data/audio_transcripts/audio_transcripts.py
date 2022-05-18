import os
import re
import gdown
import requests
import jsonlines
from align_data.common.utils import *
from tqdm import tqdm


class AudioTranscripts:
    def __init__(
        self,
        gdrive_address,
    ):
        self.name = "audio_transcripts"
        self.gdrive_address = gdrive_address

    def fetch_entries(self):
        print("Fetching alignment_newsletter entries")
        self.setup()
        self.audio_transcripts = {}
        for file in os.listdir('axrp.github.io/_posts'):
            file = 'axrp.github.io/_posts/' + file
            with open(file, 'r') as f:
                self.text = f.read()
                self.title = re.findall('(?<=- ).+(?=\")', re.findall('title: +\".+\"', self.text)[0])[0]
                self.date = file.split('/')[-1][0:10]
                try:
                    start_of_transcript = re.search('\[(Google Podcasts link)\]\((.+)\)\n\n', self.text).end()
                except: 
                    start_of_transcript = re.search('\*Audio unavailable for this episode.\*\n\n', self.text).end()
                    pass
                self.text = f"# {self.title} on the AXRP Podcast\nDate: {self.date}\n\n" + self.text[start_of_transcript:]

        for json_file in os.listdir(self.local_out):
            yield json.load(open(os.path.join(self.local_out, json_file)))

        # delete the local files
        os.system('rm -rf ' + self.local_teis)
        os.system('rm -rf ' + self.local_out)
        os.chdir(self.PROJECT_DIR)
        

    def fetch_individual_entries(self, i):
        print(f"Processing entry {i}/{len(self.num_entries)}")

        self.audio_transcripts[i] = {
            "source": "audio transcripts",
            "source_filetype": "audio",
            "converted_with": self.transcribed_with,
            "title": self.title,
            "date_published": str(self.date),
            "data_last_modified": None,
            "url": self.url,
            "alignment_newsletter_metadata": {
            "venue": None,
            "newsletter_category": None,
            "highlight": None,
            "newsletter_number": None,
            "newsletter_url": None,
            "summarizer": None,
            "opinion": None,
            "prerequisites": None,
            "individual_summary": None,
            "paper_summary": None,
            "read_more": None,
            "paper_text": None,
            },
            "paper_metadata": {
            "abstract": None,
            "arxiv_id": None,
            "authors": None,
            "author_comment": None,
            "doi": None,
            "paper_version": None,
            "primary_category": None,
            "categories": None,
            "journal_ref": None,
            "bibliography_bbl": None,
            "bibliography_bib": None,
            },
            "text": self.text,
        }

    def setup(self):
        self.PROJECT_DIR = os.getcwd()
        self.RAW_TRANSCRIPTS_DIR = os.path.join(self.PROJECT_DIR, 'data/raw/audio_transcripts/')
        sh(f"mkdir -p {self.PROJECT_DIR}/data/raw/audio_transcripts")
        if os.path.exists(f"{self.PROJECT_DIR}/data/audio_transcripts.jsonl"):
            os.remove(f"{self.PROJECT_DIR}/data/audio_transcripts.jsonl")
        if os.path.exists(f"{self.PROJECT_DIR}/data/audio_transcripts.txt"):
            os.remove(f"{self.PROJECT_DIR}/data/audio_transcripts.txt")
        self.download_transcripts()

    def download_transcripts(self):
        os.chdir(self.RAW_TRANSCRIPTS_DIR)
        if not os.path.exists('axrp.github.io'):
            os.system('git clone https://github.com/axrp/axrp.github.io')
        print('Downloading everything...')
        self.pull_from_gdrive()
        self.pull_from_otter()
        # unzip the downloaded folder
        print('Unzipping...')
        os.system('unzip -o ' + 'transcripts.zip -d ' + ".")
        # remove the zip files
        os.system('rm ' + '*.zip')
        os.chdir(self.PROJECT_DIR)

    def pull_from_gdrive(self):
        gdown.download(url=self.gdrive_address, output='transcripts.zip', quiet=False)

    def pull_from_otter(self):
        os.system('wget -O ' + 'transcripts.zip ' + self.gdrive_address)