import json
import jsonlines
import os
import logging

logger = logging.getLogger(__name__)


def add_alignment_newsletter_summaries_to_datasets(path_to_processed_jsonl: str = "processed/alignment_newsletter_separate_summaries.jsonl",
                                                   out_path: str = "data") -> None:
    alignment_newsletter_entry_list = {}
    with jsonlines.open(os.path.join(out_path, path_to_processed_jsonl)) as reader:
        for ii, obj in enumerate(reader):
            alignment_newsletter_entry_list[ii] = obj

    for dataset in ["reports", "distill", "lesswrong", "nonarxiv_papers"]:
        logger.info(f"Moving {dataset} to processed/{dataset}.jsonl")
        json_filename = os.path.join(
            out_path, "processed/jsons/", dataset + ".json")
        jsonl = os.path.join(out_path,  dataset + ".jsonl")
        with jsonlines.open(jsonl, "r") as reader:
            tmp_dict = {ii: obj for ii, obj in enumerate(reader)}
        json.dump(tmp_dict, open(json_filename, "w"))

    # Add the alignment newsletter summaries to the arxiv, distill, lesswrong, non-arxiv, and reports datasets
    logger.info("Adding alignment newsletter summaries to datasets...")
    for dataset in ["arxiv.org", "distill", "lesswrong", "nonarxiv_papers", "reports"]:
        logger.info(
            f"Adding alignment newsletter summaries to {dataset} dataset")

        json_filename = os.path.join(
            out_path, "processed/jsons/", dataset + ".json")
        jsonl = os.path.join(out_path,  dataset + ".jsonl")
        write_path = os.path.join(out_path, "processed/", dataset + ".jsonl")
        tmp_dict = json.load(open(json_filename, "r"))

        for k, entry in alignment_newsletter_entry_list.items():
            for tmp_entry in tmp_dict.values():
                if tmp_entry["title"] == entry["title"]:
                    tmp_dict[k]["alignment_newsletter"] = entry

        json.dump(tmp_dict, open(json_filename, "w"))

        for entry in tmp_dict.keys():
            with jsonlines.open(write_path, "a") as writer:
                writer.write(tmp_dict[entry])
