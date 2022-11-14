import logging
import torch

from semanticscholar import SemanticScholar
from transformers import AutoTokenizer, AutoModel

device = torch.device("mps")

# load model and tokenizer
tokenizer = AutoTokenizer.from_pretrained('allenai/specter')
model = AutoModel.from_pretrained('allenai/specter').to(device)

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
if not logger.hasHandlers():
    logger.addHandler(logging.StreamHandler())

def get_paper_from_title(title : str):
    try:
        sch = SemanticScholar()
        paper = sch.search_paper(title , limit=1) # , fields=['title' , 'paperId'])
    except Exception as e:
        logger.error(f"Error while fetching paper for {title} : {e}")
        paper = None
    return paper


def get_embedding_from_paper(papers : list):
    # concatenate title and abstract
    title_abs = [paper['title'] + tokenizer.sep_token + (paper.get('abstract') or '') for paper in papers]
    # preprocess the input
    inputs = tokenizer(title_abs, padding=True, truncation=True, return_tensors="pt", max_length=512).to(device)
    result = model(**inputs)
    # take the first token in the batch as the embedding
    embeddings = result.last_hidden_state[:, 0, :]
    return embeddings
