#%%
import os
os.chdir('/Users/janhendrikkirchner/code/2022/10/alignment-research-dataset')
#%%
import jsonlines

from path import Path
from align_data.postprocess.utils import get_embedding_from_paper
from tqdm import tqdm
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split

#%%
uber_jsonl = Path('/Users/janhendrikkirchner/code/2022/10/alignment-research-dataset/data/raw/scratch/uber-file.jsonl')

with jsonlines.open(uber_jsonl , 'r') as reader:
    all_arxiv = [obj for obj in tqdm(reader) if ('source' in obj) and (obj['source'] == 'arxiv')]
print(f"Loaded {len(all_arxiv)} papers from arxiv")
#%%
stride = 10
for ii in tqdm(range(0, len(all_arxiv), stride)):
    if 'embedding' in all_arxiv[ii]:
        continue
    embeddings = get_embedding_from_paper(papers=all_arxiv[ii:ii+stride]).detach().cpu()
    for jj, embedding in enumerate(embeddings):
        all_arxiv[ii+jj]['embedding'] = embedding.tolist()
# %%
labels = [int(obj['citation_level']) for obj in all_arxiv]
embeds = [obj['embedding'] for obj in all_arxiv]

X_train,X_test,y_train,y_test = train_test_split(embeds,1-labels,test_size=0.3,random_state=0) 
clf = LogisticRegression(max_iter=10000).fit(X_train, y_train)
#%%
import pylab as plt
from sklearn import metrics

#define metrics
y_pred_proba = clf.predict_proba(X_test)[::,1]
fpr, tpr, _ = metrics.roc_curve(y_test,  y_pred_proba)

#create ROC curve
plt.figure(figsize=(5,5))
plt.plot(fpr,tpr)
plt.ylabel('True Positive Rate')
plt.xlabel('False Positive Rate')
plt.xlim([0,1])
plt.ylim([0,1])
plt.xticks([0,1])
plt.yticks([0,1])
sns.despine()