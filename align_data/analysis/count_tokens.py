from transformers import AutoTokenizer
import jsonlines
import logging
from typing import Tuple
logger = logging.getLogger(__name__)

def count_token(merged_dataset_path : str = "data/merged_dataset/alignment_texts.jsonl") -> Tuple[int , int , int]:
    tokenizer = AutoTokenizer.from_pretrained("gpt2")
    total_token_count , total_word_count , total_character_count = 0 , 0 , 0

    with jsonlines.open(merged_dataset_path) as reader:
        for obj in reader:
            encoding = tokenizer(obj["text"])
            total_token_count += len(encoding.tokens())
            total_word_count += len(obj["text"].split())
            total_character_count += len(obj["text"])

    logger.info(f"Total token count: {total_token_count}")
    logger.info(f"Total word count: {total_word_count}")
    logger.info(f"Total character count: {total_character_count}")
    return total_token_count , total_word_count , total_character_count


