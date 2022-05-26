from .agentmodels import AgentModels
from .gdrive_ebooks import GDrive

EBOOK_REGISTRY = [
    AgentModels('https://github.com/agentmodels/agentmodels.org.git'),
    GDrive('https://drive.google.com/drive/folders/1VbVS9OzfI0Rc05NRXto3SWuqzYSNa4Hy')
]
