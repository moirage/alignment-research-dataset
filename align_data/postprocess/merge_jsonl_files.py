import jsonlines
import os
from tqdm import tqdm
import logging

logger = logging.getLogger(__name__)

def merge_all_files(out_dir : str = "data") -> str:
    # Merge all jsonl files into one big jsonl file
    if not os.path.exists(os.path.join(out_dir , "merged_dataset")): os.mkdir(os.path.join(out_dir , "merged_dataset"))

    num_entries = len(os.listdir(out_dir))
    with jsonlines.open("merged_dataset/alignment_texts.jsonl", mode="a") as writer:
        for ii , file in enumerate(tqdm(os.listdir(out_dir))):
            logger.info(f"Processing {file} ({ii}/{num_entries})")
            if file.endswith(".jsonl"):
                with jsonlines.open(file) as reader:
                    for line in reader:
                        writer.write(line)

    return os.path.join(out_dir , "merged_dataset")