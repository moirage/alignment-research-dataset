#%%

import arxiv
import torch
import pickle

import pandas as pd

from tqdm import tqdm
# from transformers import AutoTokenizer
# from sentence_transformers import SentenceTransformer
from path import Path
from datetime import datetime
#%%

device = "cuda:0" if torch.cuda.is_available() else "cpu"
tokenizer = AutoTokenizer.from_pretrained('sentence-transformers/allenai-specter')
model = SentenceTransformer('sentence-transformers/allenai-specter').to('cuda:0')
model.eval()

def get_embed(title_abs):
  return model.encode(title_abs)

#%%
log_reg_path = Path('/Users/janhendrikkirchner/code/2022/10/alignment-research-dataset/classify_scrape/model/logistic_regression.pickle')

big_slow_client = arxiv.Client(
  page_size = 1000,
  delay_seconds = 1,
  num_retries = 5
)

clf = pickle.loads(log_reg_path.bytes())

arxiv_scored_dicts = []
for result in tqdm(big_slow_client.results(arxiv.Search(query="cs.AI")) , total=50000 ):
  try:
    title_abs = result.title + tokenizer.sep_token + result.summary.replace('\n\n','<LINEBREAK>').replace('\n',' ').replace('<LINEBREAK>','\n')
    embed = get_embed(title_abs)
    score = clf.predict_proba(embed[None,...])[::,1][0]
    arxiv_scored_dicts.append({
        'title': result.title,
        'score': score,
        'date': result.published,
        'id': result.entry_id
    })
  except Exception as e:
    print(f"Failed with exception: {e}")

#%%
axiv_filter_update_path = Path(__file__).parent / 'raw' / 'arxiv_filter_updated.csv'

arxiv_scored_dicts = pd.read_csv(axiv_filter_update_path).to_dict('records')
arxiv_scored_dicts_high_score = [c_dict for c_dict in arxiv_scored_dicts if c_dict['scores'] > 0.95]
#%%
all_write_dicts = []
for c_dict in tqdm(arxiv_scored_dicts_high_score):
    search = arxiv.Search(id_list=[c_dict['ids'].split('/abs/')[1]] , max_results=1)
    paper = next(search.results())
    write_dict = {}
    write_dict['Key'] = 'XXX'
    write_dict['Item Type'] = 'journalArticle'
    write_dict['Publication Year'] = paper.published.year
    write_dict['Author'] = ', '.join(map(str , paper.authors))
    write_dict['Title'] = paper.title
    write_dict['Publication Title'] = paper.journal_ref if paper.journal_ref else ''
    write_dict['ISBN'] = ''
    write_dict['ISSN'] = ''
    write_dict['DOI'] = paper.doi if paper.doi else ''
    write_dict['Url'] = paper.entry_id
    write_dict['Abstract Note'] = paper.summary
    write_dict['Date'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    all_write_dicts.append(write_dict)
#%%

write_df = pd.DataFrame(all_write_dicts)
write_df.to_csv(Path(__file__).parent / 'raw' / 'ai-alignment-papers-update.csv' , index=False)
# Key	Item Type	Publication Year	Author	Title	Publication Title	ISBN	ISSN	DOI	Url	Abstract Note	Date	Date Added	Date Modified	Access Date
# %%
