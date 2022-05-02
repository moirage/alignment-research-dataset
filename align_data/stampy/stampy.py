from align_data.common.utils import *
import json

class Stampy():
    def __init__(self):
        self.url = "https://stampy.ai/wiki/Special:Ask/mainlabel%3D/format%3Djson/searchlabel%3DJSON/template%3DACard/userparam%3DQA/sort%3DStampCount/order%3Ddesc/offset%3D0/limit%3D500/-5B-5BCategory:Answers-5D-5D-20-5B-5BOutOfScope::false-5D-5D-20-5B-5BCanonical::true-5D-5D/-3F%3D-2D-23-2D/-3FAnswer/-3FStampedBy/-3FTags-23-2D/prettyprint%3Dtrue/unescape%3Dtrue"
        self.name = "stampy"
        self.PROJECT_DIR = os.getcwd()

    def fetch_entries(self):
        print("Fetching stampy entries")
        sh("mkdir -p data/raw/stampy")
        sh(f"wget {self.url} -O {self.PROJECT_DIR}/data/raw/stampy/stampy.json")
        with open(f"{self.PROJECT_DIR}/data/raw/stampy/stampy.json") as f:
            entries = json.load(f)
        qa_entry = {}
        for i, question in enumerate(list(entries["results"].keys())):
            qa_entry[i] = entries["results"][question]
            qa_entry[i]["question"] = ' '.join(question.split("to ")[1:])
            qa_entry[i]["answer"] = entries["results"][question]["printouts"]["Answer"]
            qa_entry[i]["text"] = "Question: " + qa_entry[i]["question"] + "\n\nAnswer: " + entries["results"][question]["printouts"]["Answer"][0]
            # if there is more than one answer, add the rest
            for i in range(1, len(entries["results"][question]["printouts"]["Answer"])):
                qa_entry[i]["text"] += f"\n\nAnswer {str(i)}: " + entries["results"][question]["printouts"]["Answer"][i]
        for i in qa_entry.keys():
            entry = qa_entry[i]
            yield entry