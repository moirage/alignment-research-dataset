#%%
import pickle
import jsonlines

import numpy as np
import pylab as plt
import seaborn as sns

from path import Path
from tqdm import tqdm

sns.set_style('ticks')

log_reg_path = Path('/Users/janhendrikkirchner/code/2022/10/alignment-research-dataset/classify_scrape/model/logistic_regression.pickle')
specter_path = Path('/Users/janhendrikkirchner/code/2022/10/alignment-research-dataset/classify_scrape/scidocs/data/specter-embeddings/user-citation.jsonl')
# %%
clf = pickle.loads(log_reg_path.bytes())
# %%
specter_dicts = []
with jsonlines.open(specter_path) as reader:
    for obj in tqdm(reader):
        score = clf.predict_proba(np.array(obj['embedding']).reshape(1,-1))[0][1]
        specter_dicts.append({
            'title': obj['title'],
            'paper_id': obj['paper_id'],
            'score': score
        })
# %%
scores = [d['score'] for d in specter_dicts]
# %%
plt.figure(figsize=(5,5))
sns.histplot(scores, bins=100)
plt.yscale('log')
# %%
match_titles_and_ids = [(d['title'], d['paper_id']) for d in specter_dicts if d['score'] > 0.999]
# %%
