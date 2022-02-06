import bs4
import jsonlines
import os
import re

class EntryWriter:
    def __init__(self, name, path):
        """
        name: name of the blog, used as the file name
        path: path to save the blog posts
        """
        if not os.path.exists(path):
            os.makedirs(path)

        jsonl_file = os.path.join(path, name + '.jsonl')
        txt_file = os.path.join(path, name + '.txt')

        self.jsonl_writer = jsonlines.open(jsonl_file, mode='w')
        self.text_writer = open(txt_file, mode='w')
        self.entry_idx = 0

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.jsonl_writer.close()
        self.text_writer.close()

    def write(self, entry):
        # Save the entry in JSONL file
        self.jsonl_writer.write(entry)

        # Save the entry in plain text, mainly for debugging
        print("[ENTRY {}]".format(self.entry_idx), file=self.text_writer)
        text = '    '.join(('\n'+entry["text"].lstrip()).splitlines(True)) + '\n'
        print(text, file=self.text_writer)

        self.entry_idx += 1

class HtmlCleaner:
    def __init__(self, rgx_list):
        """
        rgx_list: list of regexes to strip from the HTML
        """
        self.regexes = [re.compile(r) for r in rgx_list]

    def clean(self, html):
        soup = bs4.BeautifulSoup(html, features="html.parser")
        text = soup.get_text()
        for rgx in self.regexes:
            text = rgx.sub("", text)

        return text
