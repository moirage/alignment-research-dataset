from .agentmodels import AgentModels
from .gdrive_ebooks import GDrive
from .mdebooks import MDEBooks

EBOOK_REGISTRY = [
    AgentModels(name='agentmodels',
                repo='https://github.com/agentmodels/agentmodels.org.git'),
    GDrive(name='gdrive_ebooks',
           gdrive_adress='https://drive.google.com/drive/folders/1VbVS9OzfI0Rc05NRXto3SWuqzYSNa4Hy'),
    MDEBooks(name="markdown.ebooks",
             gdrive_address="https://drive.google.com/uc?id=1jRtk3LSa1cWxAYu0DO0VGFY-J710FCfB"),
]
