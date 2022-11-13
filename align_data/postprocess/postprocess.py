#%%
from dataclasses import dataclass
import jsonlines
from tqdm import tqdm
import logging
from path import Path

import pylab as plt
# import seaborn as sns
import pandas as pd

logger = logging.getLogger(__name__)

@dataclass
class PostProcesser:
    """
    This class is used to postprocess the data
    """
    jsonl_path : Path = Path('../../data/')

    def __init__(self) -> None:
        self.jsonl_list = sorted(self.jsonl_path.files('*.jsonl'))
        self.source_list = [path.name.split('.jsonl')[0] for path in self.jsonl_list]

    def compute_statistics(self) -> None:
        self.all_stats = {key : {} for key in self.source_list}
        for source_name , path in tqdm(zip(self.source_list , self.jsonl_list)):
            with jsonlines.open(path) as reader:
                for obj in reader:
                    self.all_stats[source_name]['num_entries'] = self.all_stats[source_name].get('num_entries' , 0) + 1
                    self.all_stats[source_name]['num_tokens'] = self.all_stats[source_name].get('num_tokens' , 0) + len(obj['text'].split())
                    self.all_stats[source_name]['num_chars'] = self.all_stats[source_name].get('num_chars' , 0) + len(obj['text'])
                    self.all_stats[source_name]['num_words'] = self.all_stats[source_name].get('num_words' , 0) + len(obj['text'].split())
                    self.all_stats[source_name]['num_sentences'] = self.all_stats[source_name].get('num_sentences' , 0) + len(obj['text'].split('.'))
                    self.all_stats[source_name]['num_paragraphs'] = self.all_stats[source_name].get('num_paragraphs' , 0) + len(obj['text'].splitlines())
        
    def plot_statistics(self) -> None:
        all_df = pd.DataFrame(self.all_stats).T
        plt.figure(figsize = (5 , 5))
        sns.barplot(x = all_df.index , y = all_df['num_entries'])
        

    def merge_all_files(self , out_dir : str) -> str:
        pass

    def deduplicate(self) -> None:
        for path in tqdm(self.jsonl_list):
            with jsonlines.open(path , 'r') as reader:
                all_obj = {obj['id'] : obj for obj in reader}
            with jsonlines.open(path , 'w') as writer:
                for obj in all_obj.values():
                    writer.write(obj)

    def clean_dataset(self , merged_dataset_path : str) -> str:
        pass

pp = PostProcesser()
# %%
pp.source_list
# %%
pp.compute_statistics()
# %%
pp.deduplicate()
# %%
