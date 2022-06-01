import jsonlines
import os

# Merge all jsonl files into one big jsonl file
os.chdir("data")
with jsonlines.open("all_alignment_texts.jsonl", mode="w") as writer:
    for file in os.listdir("."):
        if file.endswith(".jsonl"):
            with jsonlines.open(file) as reader:
                for line in reader:
                    writer.write(line)
