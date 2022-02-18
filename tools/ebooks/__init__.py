from pprint import pprint
from .agentmodels import AgentModels
from .gdrive_ebooks import GDrive

EBOOK_REGISTRY = [
    AgentModels('https://github.com/agentmodels/agentmodels.org.git'),
    GDrive('https://drive.google.com/drive/folders/1VbVS9OzfI0Rc05NRXto3SWuqzYSNa4Hy')
]

ALL_EBOOKS = sorted([ebook.name for ebook in EBOOK_REGISTRY])
EBOOK_MAP = dict([(ebook.name, ebook) for ebook in EBOOK_REGISTRY])

def get_ebook(ebook_name):
    try:
        return EBOOK_MAP[ebook_name]
    except KeyError as e:
        print("Available ebooks:")
        pprint(ALL_EBOOKS)
        raise KeyError(f"Missing ebook {ebook_name}")
