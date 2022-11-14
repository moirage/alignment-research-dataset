#%%
import torch
import pickle

from datasets import load_dataset
from transformers import AutoTokenizer
from sentence_transformers import SentenceTransformer
from path import Path
from tqdm import tqdm
#%%
wiki_data = load_dataset("wikipedia", "20220301.en")
# %%
log_reg_path = Path('/Users/janhendrikkirchner/code/2022/10/alignment-research-dataset/classify_scrape/model/logistic_regression.pickle')

clf = pickle.loads(log_reg_path.bytes())
#%%
device = "mps" if torch.backends.mps.is_available() else "cpu"
tokenizer = AutoTokenizer.from_pretrained('sentence-transformers/allenai-specter')
model = SentenceTransformer('sentence-transformers/allenai-specter')
model.eval()

def get_embed(title_abs):
  return model.encode(title_abs)
# %%
all_scored_dicts = []
for data in tqdm(wiki_data['train']):
    title_abs = data['title'] + tokenizer.sep_token + data['text'].splitlines()[0]
    embed = get_embed(title_abs)
    score = clf.predict_proba(embed[None,...])[::,1][0]
    # dict_keys(['id', 'url', 'title', 'text'])
    if score < 0.95:
        continue
    all_scored_dicts.append({
        'title': data['title'],
        'score': score,
        'id': data['id'],
        'url': data['url'],
        'text': data['text']
    })
# %%
