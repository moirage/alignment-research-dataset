import jsonlines
import os
from tqdm import tqdm

# Merge all jsonl files into one big jsonl file
os.chdir("data")
os.makedirs("merged_dataset", exist_ok=True)
num_entries = len(os.listdir("."))
i = 0
with jsonlines.open("merged_dataset/alignment_texts.jsonl", mode="a") as writer:
    for file in tqdm(os.listdir(".")):
        print(f"Processing {i}/{num_entries}")
        print(file)
        i += 1
        if file.endswith(".jsonl"):
            with jsonlines.open(file) as reader:
                for line in reader:
                    writer.write(line)
