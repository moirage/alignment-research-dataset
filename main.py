from dataclasses import dataclass
import os
import fire
from dataclasses import dataclass
from typing import List , Union
import align_data
from align_data.common.utils import EntryWriter
from align_data.analysis.count_tokens import count_token

# import logging , sys

# logging.basicConfig(stream=sys.stdout, level=logging.INFO)

@dataclass
class AlignmentDataset:

    out_path : str = "data"

    def cmd_list(self) -> List[str]:
        """
        `cmd_list` is a function that takes in a self parameter and returns a list of strings
        :return: A list of all the datasets
        """
        for name in align_data.ALL_DATASETS:
            print(name)
        return align_data.ALL_DATASETS

    def cmd_fetch(self , name) -> None:
        """
        > This function takes a dataset name and writes the entries of that dataset to a file
        
        :param name: The name of the dataset to fetch
        :return: The path to the file that was written to.
        """
        assert name in align_data.ALL_DATASETS , f"{name} is not a valid dataset name"
        with EntryWriter(name, self.out_path) as writer:
            for entry in align_data.get_dataset(name).fetch_entries():
                writer.write(entry)

        return os.path.join(self.out_path, name + ".jsonl")

    def cmd_fetch_all(self) -> str:
        """
        It downloads all the datasets, moves the alignment_newsletter.jsonl file to the processed
        folder, deletes the alignment_newsletter.jsonl file, adds the alignment_newsletter_summaries to
        the datasets, and merges all the files
        :return: The path to the merged file.
        """
        for name in align_data.ALL_DATASETS:
            print(name)
            self.cmd_fetch(name)
        
        return None #merge_all_files(out_dir = self.out_path)

    def cmd_count_tokens(self , merged_dataset_path : str) -> None:
        """
        This function counts the number of tokens, words, and characters in the dataset
        :return: None
        """
        assert os.path.exists(merged_dataset_path) , "The path to the merged dataset does not exist"
        count_token(merged_dataset_path)

def main(command : str , out_path : str = "data" , dataset_name : str = None ) -> Union[str , List[str] , None]:
    """
    It downloads the alignment dataset from the internet and saves it to a local directory
    
    :param command: The command to run. Can be one of: list, fetch, fetch_all, count_tokens
    :type command: str
    :param out_path: The path to the directory where the data will be downloaded, defaults to data
    :type out_path: str (optional)
    :param dataset_name: The name of the dataset to fetch
    :type dataset_name: str
    :return: A list of strings.
    """

    assert command in [ "list" , "fetch" , "fetch-all" ] , f"Invalid command: {command}"

    al_dataset = AlignmentDataset(out_path)

    if command == "list":
        return al_dataset.cmd_list()
    elif command == "fetch":
        return al_dataset.cmd_fetch(dataset_name)
    elif command == "fetch-all":
        return al_dataset.cmd_fetch_all()
    elif command == "count-tokens":
        al_dataset.cmd_count_tokens()
        return None

if __name__ == "__main__":
    fire.Fire(main)
