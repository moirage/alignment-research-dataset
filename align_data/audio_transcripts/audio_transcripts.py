from dataclasses import dataclass, field
import gdown
from align_data.common.alignment_dataset import AlignmentDataset , DataEntry
from typing import List
import zipfile
import os
import logging
import sys
import re

logging.basicConfig(format='%(asctime)s | %(levelname)s : %(message)s',
                    level=logging.INFO, stream=sys.stdout)
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

@dataclass
class AudioTranscripts(AlignmentDataset):

    otter_zip_url : str 
    transcript_path : str = "."

    def __post_init__(self):
        self.setup()
        if not os.path.exists(self.transcript_path):
            self._pull_from_gdrive()
        self.file_list = [xx for xx in os.listdir(os.path.join(self.transcript_path , 'transcripts')) if xx.endswith('.md')]


    def _pull_from_gdrive(self):
        logger.info("Pulling from gdrive")
        gdown.download(url=self.otter_zip_url, 
                       output=os.path.join(self.transcript_path, "transcripts.zip"), 
                       quiet=False)
        logger.info("Unzipping")
        with zipfile.ZipFile(os.path.join(self.transcript_path, "transcripts.zip"), 'r') as zip_ref:
            zip_ref.extractall(self.transcript_path)
            
            
    
    def fetch_entries(self):
        for ii, filename in enumerate(self.file_list):
            if self._entry_done(ii):
                logger.info(f"Already done {ii}")
                continue
            
            logger.info(f"Processing {filename}")
            text = open(os.path.join(self.transcript_path, 'transcripts', filename), "r").read()
            title = filename.split(".")[0]
            
            date = re.search(r"\d{4}\d{2}\d{2}", filename).group(0)
            date = date[:4] + "-" + date[4:6] + "-" + date[6:]
            
            new_entry = DataEntry({
                "source": "audio-transcripts",
                "source_filetype": "audio",
                "url": "n/a",
                "converted_with": "otter-ai",
                "title": title,
                "authors": "unknown",
                "date_published": str(date),
                "text": text,
            })
            new_entry.add_id()
            yield new_entry            

        # raise NotImplementedError



    # def __init__(
    #     self,
    #     gdrive_address,
    #     name,
    #     gdown_folder_name,
    #     is_cleaned,
    #     authors=None,
    # ):
    #     self.name = name
    #     self.gdrive_address = gdrive_address
    #     self.folder_name = gdown_folder_name
    #     self.is_cleaned = is_cleaned
    #     self.authors = ""
    #     self.entries = {}

    # def fetch_entries(self):
    #     print(f"Fetching {self.name} entries")
    #     self.setup()
    #     self.folder_name = self.RAW_TRANSCRIPTS_DIR + "/" + self.folder_name
    #     self.download_transcripts()

    #     # create dictionary to store the entries
    #     self.num_entries = len(os.listdir(self.folder_name))
    #     print(list(os.listdir(self.folder_name)))
    #     print("-------------------------------")
    #     print(self.folder_name)
    #     for i, file in enumerate(os.listdir(self.folder_name)):
    #         if file.endswith(".md"):
    #             file = os.path.join(self.folder_name, file)
    #             self.fetch_individual_entries(i, file)

    #     os.makedirs("data/processed/jsons/audio_transcripts", exist_ok=True)

    #     json.dump(
    #         self.entries,
    #         open(f"data/processed/jsons/audio_transcripts/{self.name}.json", "w"),
    #     )
    #     print(f"Finished updating {self.name}.json.")

    #     print(
    #         f"Converting {self.name}.json to {self.name}.jsonl and {self.name}.txt..."
    #     )
    #     for k in self.entries.keys():
    #         yield self.entries[k]

    # def fetch_individual_entries(self, i, filepath):
    #     print(f"Processing entry {i}/{self.num_entries}")
    #     filename = filepath.split("/")[-1]
    #     # grab the title by opening the .md file and grabbing the text in between ## and \n
    #     with open(filepath, "r") as f:
    #         text = f.read()
    #     title = re.search(r"^#\s(.*)\n$", text, re.MULTILINE).group(1)
    #     print(filename)
    #     date = re.search(r"\d{4}\d{2}\d{2}", filename).group(0)
    #     date = date[:4] + "-" + date[4:6] + "-" + date[6:]
    #     try:
    #         authors = re.search(r"-by\s(.*)-video", filename).group(1)
    #     except:
    #         try:
    #             authors = re.search(r"-by\s(.*)-date", filename).group(1)
    #         except:
    #             print("Could not find authors")
    #             authors = ""

    #     self.entries[i] = {
    #         "source": "audio-transcripts",
    #         "source_filetype": "audio",
    #         "cleaned": self.is_cleaned,
    #         # "audio_category": self.category,  # podcast, lecture, educational (Rob Miles),
    #         "converted_with": "otter-ai"
    #         if self.name == "otter_ai_cleaned_transcripts"
    #         else "not converted",
    #         "title": title,
    #         "authors": authors,
    #         "date_published": str(date),
    #         "text": text,
    #     }

    # def setup(self):
    #     self.PROJECT_DIR = os.getcwd()
    #     self.RAW_TRANSCRIPTS_DIR = os.path.join(
    #         self.PROJECT_DIR, "data/raw/audio_transcripts"
    #     )
    #     sh(f"mkdir -p {self.RAW_TRANSCRIPTS_DIR}")

    # def download_transcripts(self):
    #     os.makedirs(self.RAW_TRANSCRIPTS_DIR, exist_ok=True)
    #     os.chdir(self.RAW_TRANSCRIPTS_DIR)
    #     print("Downloading everything...")
    #     if self.name == "otter_ai_cleaned_transcripts":
    #         self.pull_from_otter()
    #     else:
    #         self.pull_from_gdrive()
    #     # unzip the downloaded folder
    #     print("Unzipping...")
    #     os.system("unzip -o " + "transcripts.zip -d " + ".")
    #     # remove the zip files
    #     os.system("rm " + "*.zip")
    #     os.chdir(self.PROJECT_DIR)


    # def pull_from_otter(self):
    #     os.system("wget -O " + "otter_transcripts.zip " + self.gdrive_address)
