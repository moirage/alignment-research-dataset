import glob
import os
import tempfile
import typing
from git import Repo
from align_data import templates


class AgentModels(templates.Dataset):
    """
    Grabs the "Modeling Agents with Probabilistic Programs" by Owain Evans, Andreas Stuhlmüller,
    John Salvatier, and Daniel Filan as .md from GitHub
    """

    name = 'agentmodels.org'

    def __init__(self, url='https://github.com/agentmodels/agentmodels.org.git'):
        self.url = url 

    def fetch_entries(self) -> typing.Iterable[dict]:
        with tempfile.TemporaryDirectory() as to_path:
            md_path = to_path + '/agentmodels_markdown'
            if not os.path.exists(md_path):
                os.makedirs(md_path)
            Repo.clone_from(self.url, to_path + '/agentmodels.org')
            os.system('mv ' + to_path + '/agentmodels.org/chapters/*.md ' + md_path)
            os.system('rm -rf ' + to_path + '/agentmodels.org')
            full_book = ''
            for filename in glob.iglob(os.path.join(md_path, '*.md')):
                with open(filename, 'r') as file:
                    full_book += file.read().replace('\n', '')
        yield {
            'content': '',  # NOTE: The raw content may be too expensive to store for each book.
            'text': full_book,
            'metadata': {
                'source': 'GitHub',
                'source_filetype': 'markdown',
                'converted_with': 'not converted',
                'book_title': 'Modeling Agents with Probabilistic Programs',
                'author': ['Owain Evans', 'Andreas Stuhlmüller', 'John Salvatier', 'Daniel Filan'],
                'date_published': '2016'
            }
        }
