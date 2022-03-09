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

    def fetch(self, to_path='data/ebooks'):
        if not os.path.exists(to_path):
            os.makedirs(to_path)
        if not os.path.exists(to_path + '/agentmodels_markdown'):
            os.makedirs(to_path + '/agentmodels_markdown')
        Repo.clone_from(self.repo, to_path+'/agentmodels.org') 
        os.system('mv ' + to_path +'/agentmodels.org/chapters/*.md ' + to_path + '/agentmodels_markdown')
        os.system('rm -rf ' + to_path + '/agentmodels.org')
        for filename in glob.iglob(os.path.join(to_path + '/agentmodels_markdown', '*.md')):
            os.rename(filename, filename[:-3] + '.txt')
        
    
