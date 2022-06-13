import os
from transformers import AutoTokenizer
import jsonlines

tokenizer = AutoTokenizer.from_pretrained("gpt2")
total_token_count = 0
total_word_count = 0
total_character_count = 0

with jsonlines.open("data/merged_dataset/alignment_texts.jsonl") as reader:
    for obj in reader:
        encoding = tokenizer(obj["text"])
        total_token_count += len(encoding.tokens())
        total_word_count += len(obj["text"].split())
        total_character_count += len(obj["text"])

print("Total token count:", total_token_count)
print("Total word count:", total_word_count)
print("Total character count:", total_character_count)
