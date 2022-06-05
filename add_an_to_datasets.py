import json
import jsonlines

alignment_newsletter_entry_list = {}
i = 0
with jsonlines.open(
    "data/processed/alignment_newsletter_separate_summaries.jsonl"
) as reader:
    for obj in reader:
        alignment_newsletter_entry_list[i] = obj
        i += 1

for dataset in ["reports", "distill", "lesswrong", "nonarxiv_papers"]:
    i = 0
    tmp_dict = {}
    json_filename = "data/processed/jsons/" + dataset + ".json"
    jsonl = "data/" + dataset + ".jsonl"
    with jsonlines.open(jsonl, "r") as reader:
        for obj in reader:
            tmp_dict[i] = obj
            i += 1

    json.dump(tmp_dict, open(json_filename, "w"))

# Add the alignment newsletter summaries to the arxiv, distill, lesswrong, non-arxiv, and reports datasets
print("Adding alignment newsletter summaries to datasets...")
for dataset in [
    "arxiv.org",
    "distill",
    "lesswrong",
    "nonarxiv_papers",
    "reports",
]:
    json_filename = "data/processed/jsons/" + dataset + ".json"
    jsonl = "data/" + dataset + ".jsonl"
    tmp_dict = json.load(open(json_filename, "r"))
    for i in alignment_newsletter_entry_list:
        entry = alignment_newsletter_entry_list[i]
        for k in tmp_dict.keys():
            tmp_entry = tmp_dict[k]
            if tmp_entry["title"] == entry["title"]:
                tmp_dict[k]["alignment_newsletter"] = entry

                # input("Press Enter to continue...")

    json.dump(tmp_dict, open(json_filename, "w"))
    tmp_dict = json.load(open(json_filename, "r"))
    for entry in tmp_dict.keys():
        with jsonlines.open(f"data/processed/{dataset}.jsonl", "a") as writer:
            writer.write(tmp_dict[entry])
