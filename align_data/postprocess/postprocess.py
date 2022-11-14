#%%
import logging
import jsonlines

import pylab as plt
import seaborn as sns
import pandas as pd

from dataclasses import dataclass
from tqdm import tqdm
from path import Path
from transformers import AutoTokenizer
from cleantext import clean
from lxml.html.soupparser import fromstring

logger = logging.getLogger(__name__)

@dataclass
class PostProcesser:
    """
    This class is used to postprocess the data
    """
    jsonl_path : Path = Path(__file__).parent.parent.parent / 'data'
    tokenizer : AutoTokenizer = AutoTokenizer.from_pretrained("bert-base-uncased")

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


    def clean_dataset(self) -> str:
        for path in tqdm(self.jsonl_list):
            with jsonlines.open(path , 'r') as reader:
                
                for obj in reader:
                    if not 'javascript' in obj['text'].lower(): continue
                    # if not 'arxiv' in obj['source']: continue
                    if 'n/a' in obj['text']: continue
                    clean_text = self._normalize(obj['text'])
                    return obj['text'] , clean_text

    def _normalize(self , text : str) -> str:
        clean_text = clean(text,
                    fix_unicode=True,               # fix various unicode errors
                    to_ascii=False,                  # transliterate to closest ASCII representation
                    lower=False,                     # lowercase text
                    no_line_breaks=False,           # fully strip line breaks as opposed to only normalizing them
                    normalize_whitespace=False,      # replace all non-breaking spaces with normal spaces
                    no_urls=False,                  # replace all URLs with a special token
                    no_emails=True,                # replace all email addresses with a special token
                    no_phone_numbers=True,         # replace all phone numbers with a special token
                    no_numbers=False,               # replace all numbers with a special token
                    no_digits=False,                # replace all digits with a special token
                    no_currency_symbols=False,      # replace all currency symbols with a special token
                    no_punct=False,                 # remove punctuations
                    replace_with_email="<EMAIL>",
                    replace_with_phone_number="<PHONE>",
                    lang="en"                       # set to 'de' for German special handling
                )
        # clean_text = '\n'.join([line for line in clean_text.splitlines() if len(line) > 0])
        return clean_text

pp = PostProcesser()
# %%
pp.source_list
# %%
pp.compute_statistics()
# %%
pp.deduplicate()
# %%
text , clean_text = pp.clean_dataset()
# %%
print(text , clean_text)
# %%
print(pp.strip_javascript(text))
# %%
