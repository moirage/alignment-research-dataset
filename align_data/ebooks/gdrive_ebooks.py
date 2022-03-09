import os , gdown , pypandoc , re , epub_meta , json
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
        #os.system('mv ' + self.local_out + 'AIS_scrape/* ' + self.local_out)
        #os.system('rm -r ' + self.local_out + 'AIS_scrape')
        self.AIS_scrape_local = os.listdir(self.local_out)

    def augment_metadata(self , metadata):
        metadata['source'] = 'ebook'
        metadata['source_filetype'] = 'epub'
        metadata['converted_with'] = 'pandoc'
        metadata['book_title'] = metadata['title']
        metadata['author'] = metadata['authors']
        metadata['date_published'] = metadata['publication_date']
        metadata['chapter_names'] = [chap['title'] for chap in metadata['toc']]
        metadata.pop('cover_image_content')
        return metadata

    def convert_to_txt(self):
        for fName in self.AIS_scrape_local:
            newName = slugify(fName[:20])
            if 'epub' in fName and not os.path.exists(self.local_out + newName):
                os.rename( self.local_out + fName , self.local_out + 'tmp.epub')
                # convert to plain text
                output = pypandoc.convert_file(self.local_out + 'tmp.epub', 'plain',
                                               outputfile=self.local_out + 'tmp.txt')
                metadata = epub_meta.get_epub_metadata(self.local_out + 'tmp.epub')
                metadata = self.augment_metadata(metadata)
                # remove linebreaks in middle of sentence
                os.system("awk ' /^$/ { print; } /./ { printf(\"%s \", $0); } ' " + self.local_out + "tmp.txt > " + self.local_out + newName + '.txt')
                with open(self.local_out + newName + '.json', 'w') as fp:
                  json.dump(metadata, fp)
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
        self.AIS_scrape_local = os.listdir(self.local_out)

    def jsonify_everything(self):
      for fName in self.AIS_scrape_local:
            if 'txt' in fName:
              with open(self.local_out + fName[:-3] + 'json' , 'r') as json_file:
                metadata = json.load(json_file)
              with open(self.local_out + fName , 'r') as text_file:
                contents = text_file.read()
              metadata["contents"] = contents
              with open(self.local_out + fName[:-3] + 'json', 'w') as json_file:
                  json.dump(metadata, json_file)
              os.system('rm ' + self.local_out + fName)
      self.AIS_scrape_local = os.listdir(self.local_out)
                
    def merge_everything(self):
        ebook_dict = {}
        for fName in self.AIS_scrape_local:
            if 'json' in fName:
              with open(self.local_out + fName , 'r') as json_file:
                ebook = json.load(json_file)
              ebook_dict[abs(hash(ebook["book_title"]))] = ebook
              os.system('rm ' + self.local_out + fName)
        with open(self.local_path + 'all_ebooks.json', 'w') as json_file:
              json.dump(ebook_dict, json_file)
        self.AIS_scrape_local = os.listdir(self.local_out)

    def fetch(self):
        print('Downloading everything...')
        self.pull_drom_gdrive()
        print('Converting to text...')
        self.convert_to_txt()
        print('Cleaning text...')
        self.clean_txt()
        print('Converting to json...')
        self.jsonify_everything()
        print('Merging into single json...')
        self.merge_everything()
