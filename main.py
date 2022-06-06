import argparse
import jsonlines
import os
from collections import OrderedDict
from urllib.parse import urlparse

import align_data
from align_data.common.utils import EntryWriter


def cmd_list(args):
    for name in align_data.ALL_DATASETS:
        print(name)


def cmd_fetch(args):
    with EntryWriter(args.name, args.path) as writer:
        for entry in align_data.get_dataset(args.name).fetch_entries():
            writer.write(entry)


def cmd_fetch_all(args):
    for name in align_data.ALL_DATASETS:
        print(name)
        if not os.path.exists(os.path.join(args.path, name + ".jsonl")):
            with EntryWriter(name, args.path) as writer:
                for entry in align_data.get_dataset(name).fetch_entries():
                    writer.write(entry)


def create_arg_parser():
    parser = argparse.ArgumentParser(description="Fetch datasets.")
    subparsers = parser.add_subparsers(
        title="commands", description="valid commands", help="additional help"
    )

    list_cmd = subparsers.add_parser("list", help="List available datasets.")
    list_cmd.set_defaults(func=cmd_list)

    fetch_cmd = subparsers.add_parser("fetch", help="Fetch datasets.")
    fetch_cmd.set_defaults(func=cmd_fetch)
    fetch_cmd.add_argument("name", help="Name of dataset to fetch.")
    fetch_cmd.add_argument("--path", default="data", help="Path to save datasets.")

    fetch_all_cmd = subparsers.add_parser("fetch-all", help="Fetch all datasets.")
    fetch_all_cmd.set_defaults(func=cmd_fetch_all)
    fetch_all_cmd.add_argument("--path", default="data", help="Path to save datasets.")

    return parser


def main():
    parser = create_arg_parser()
    args = parser.parse_args()

    if getattr(args, "func", None) is None:
        # No subcommand was given
        parser.print_help()
        return

    args.func(args)

    os.system(
        "mv data/alignment_newsletter_separate_summaries.jsonl data/processed/alignment_newsletter_separate_summaries.jsonl"
    )
    os.system("rm data/alignment_newsletter.jsonl")
    os.system("python3 add_an_to_datasets.py")
    os.system("python3 merge_jsonl_files.py")


if __name__ == "__main__":
    main()
