from git import Repo
import os , glob
class AgentModels:
    """
    Grabs the "Modeling Agents with Probabilistic Programs" by Owain Evans, Andreas Stuhlmüller,
    John Salvatier, and Daniel Filan as .md from GitHub
    """
    def __init__(self , repo='https://github.com/agentmodels/agentmodels.org.git'):
        self.repo = repo
        self.name = 'agentmodels.org'

    def fetch_entries(self, to_path='data/ebooks'):
        if not os.path.exists(to_path):
            os.makedirs(to_path)
        if not os.path.exists(to_path + '/agentmodels_markdown'):
            os.makedirs(to_path + '/agentmodels_markdown')
        Repo.clone_from(self.repo, to_path+'/agentmodels.org') 
        os.system('mv ' + to_path +'/agentmodels.org/chapters/*.md ' + to_path + '/agentmodels_markdown')
        os.system('rm -rf ' + to_path + '/agentmodels.org')
        full_book = ''
        for filename in glob.iglob(os.path.join(to_path + '/agentmodels_markdown', '*.md')):
            with open(filename, 'r') as file:
                full_book += file.read().replace('\n', '')
        os.system('rm -rf ' + to_path)
        metadata = {}
        metadata['source'] = 'GitHub'
        metadata['source_filetype'] = 'markdown'
        metadata['converted_with'] = 'not converted'
        metadata['book_title'] = 'Modeling Agents with Probabilistic Programs'
        metadata['authors'] = ['Owain Evans', 'Andreas Stuhlmüller', 'John Salvatier', 'Daniel Filan']
        metadata['date_published'] = '2016'
        metadata['text'] = full_book
        yield metadata

        
    
