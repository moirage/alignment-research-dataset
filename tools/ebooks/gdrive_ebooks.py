import os , gdown , pypandoc , re
from .utils import slugify
class GDrive:
    """
    Pull .epubs from a Google Drive and convert them to .txt
    """
    def __init__(self , gdrive_adress):
        self.name = 'gdrive-epubs'
        self.gdrive_adress = gdrive_adress
        self.local_path = 'data/ebooks/'
        self.local_out = self.local_path + 'books_text/'
        os.makedirs(self.local_path) if not os.path.exists(self.local_path) else ''
        os.makedirs(self.local_out) if not os.path.exists(self.local_out) else ''
        self.AIS_scrape_local = os.listdir(self.local_out)
        self.weblink_pattern = r"(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'\".,<>?«»“”‘’]))"

        if os.path.exists(os.getcwd()+'/pandoc/pandoc'):
            os.environ.setdefault('PYPANDOC_PANDOC', os.getcwd()+'/pandoc/pandoc')

    def pull_drom_gdrive(self):
        gdown.download_folder(url=self.gdrive_adress, output=self.local_out, quiet=False)
        self.AIS_scrape_local = os.listdir(self.local_out)

    def convert_to_txt(self):
        for fName in self.AIS_scrape_local:
            newName = slugify(fName[:20])
            if 'epub' in fName and not os.path.exists(self.local_out + newName):
                os.rename( self.local_out + fName , self.local_out + 'tmp.epub')
                # convert to plain text
                output = pypandoc.convert_file(self.local_out + 'tmp.epub', 'plain',
                                               outputfile=self.local_out + 'tmp.txt')
                # remove linebreaks in middle of sentence
                os.system("awk ' /^$/ { print; } /./ { printf(\"%s \", $0); } ' " + self.local_out + "tmp.txt > " + self.local_out + newName + '.txt')
        os.system('rm ' + self.local_out + "tmp.txt")
        os.system('rm ' + self.local_out + "tmp.epub")
        self.AIS_scrape_local = os.listdir(self.local_out)

    def clean_txt(self , min_length=10):
        # remove short lines and replace links
        for fName in self.AIS_scrape_local:
            if 'txt' in fName:
                os.rename(self.local_out + fName , self.local_out + 'tmp.txt')
                with open(self.local_out + 'tmp.txt') as f, open(self.local_out + fName,'w') as f2:
                    for x in f:
                        stripped_x = re.sub(r'http\S+' , 'ʬ' , x);
                        if len(stripped_x) >= min_length:
                            f2.write(stripped_x)
        os.system('rm ' + self.local_out + "tmp.txt")

    def fetch(self):
        self.pull_drom_gdrive()
        self.convert_to_txt()
        self.clean_txt()

            