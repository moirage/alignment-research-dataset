import json
import jsonlines


distill_dict = {}
i = 0
with jsonlines.open("distill.jsonl") as reader:
    for obj in reader:
        # distill_dict[i] = obj
        i += 1

print(len(distill_dict))
