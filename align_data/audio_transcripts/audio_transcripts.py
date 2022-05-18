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
        n_threads=1,
    ):
        self.n_threads = n_threads
        self.name = "audio_transcripts"

    def fetch_entries(self):
        print("Fetching alignment_newsletter entries")
        self.setup()
        self.audio_transcripts = {}
        

    def fetch_individual_entries(self, i, row):
        print(f"Processing entry {i}/{len(self.df)}")

        self.audio_transcripts[i] = {
            "source": "audio transcripts",
            "source_filetype": "google drive, github, otter ai, youtube, etc.",
            "converted_with": "transcribed with otter ai or no conversion",
            "title": title,
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
            "primary_category": str(paper.primary_category) if abs != "" else "",
            "categories": str(paper.categories) if abs != "" else "",
            "journal_ref": None,
            "bibliography_bbl": None,
            "bibliography_bib": None,
            },
            "date_published": str(date_published),
            "data_last_modified": "",
            "url": url,
            "text": text,
        }

    def setup(self):
        self.PROJECT_DIR = os.getcwd()
        sh(f"mkdir -p {self.PROJECT_DIR}/data/raw/audio_transcripts")
        if os.path.exists(f"{self.PROJECT_DIR}/data/audio_transcripts.jsonl"):
            os.remove(f"{self.PROJECT_DIR}/data/audio_transcripts.jsonl")
        if os.path.exists(f"{self.PROJECT_DIR}/data/audio_transcripts.txt"):
            os.remove(f"{self.PROJECT_DIR}/data/audio_transcripts.txt")
        self.download_transcripts()

    def download_transcripts(self):
        if not os.path.exists('axrp.github.io'):
            os.system('git clone https://github.com/axrp/axrp.github.io')
        for file in os.listdir('axrp.github.io/_posts'):
            file = 'axrp.github.io/_posts/' + file
            with open(file, 'r') as f:
                text = f.read()
                title = re.findall('(?<=- ).+(?=\")', re.findall('title: +\".+\"', text)[0])[0]
                date = file.split('/')[-1][0:10]
                try:
                    start_of_transcript = re.search('\[(Google Podcasts link)\]\((.+)\)\n\n', text).end()
                except: 
                    start_of_transcript = re.search('\*Audio unavailable for this episode.\*\n\n', text).end()
                    pass
                text = f"# {title} on the AXRP Podcast\nDate: {date}\n\n" + text[start_of_transcript:]


        print(text)
