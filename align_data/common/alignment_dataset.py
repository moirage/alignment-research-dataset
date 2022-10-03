from dataclasses import dataclass


@dataclass
class AlignmentDataset:
    write_jsonl_path : str
    name : str

    def __str__(self) -> str:
        return f"{self.name} dataset will be written to {self.write_jsonl_path}"

    def fetch_entries(self):
        raise NotImplementedError

    def _entry_done(self , entry):
        raise NotImplementedError

