import gdown
import json
import os
from align_data.common.paper2json.tei2json import convert_folder_to_json


class Reports:
    def __init__(self, gdrive_adress):
        self.name = "reports"
        self.gdrive_adress = gdrive_adress
        self.local_path = "data/reports/"
        self.local_teis = self.local_path + "report_teis/"
        self.local_out = self.local_path + "report_jsons/"

    def fetch_entries(self):
        os.makedirs(self.local_path) if not os.path.exists(self.local_path) else ""
        os.makedirs(self.local_out) if not os.path.exists(self.local_out) else ""

        print("Downloading everything...")
        self.pull_from_gdrive()
        # unzip the downloaded folder
        print("Unzipping...")
        os.system(
            "unzip -o " + self.local_path + "report_teis.zip -d " + self.local_path
        )
        # remove the zip files
        os.system("rm " + self.local_path + "*.zip")

        print("converting to json...")
        convert_folder_to_json(self.local_teis, self.local_out, source=self.name)

        for json_file in os.listdir(self.local_out):
            yield json.load(open(os.path.join(self.local_out, json_file)))

        # delete the local files
        os.system("rm -rf " + self.local_teis)
        os.system("rm -rf " + self.local_out)

    def pull_from_gdrive(self):
        gdown.download(
            url=self.gdrive_adress,
            output=self.local_path + "report_teis.zip",
            quiet=False,
        )
