from bs4 import BeautifulSoup
from markdownify import MarkdownConverter
import os
import json
import pprint


class Distill:
    def __init__(self, name):
        self.name = name
        self.entries = {}

    def fetch_entries(self):
        print(f"Fetching {self.name} entries")

        DISTILL_POSTS_DIR = "align_data/distill/distill_posts/"

        self.convert_distill_dir2jsonl_file(
            DISTILL_POSTS_DIR, "data/distill_posts.jsonl"
        )

        os.makedirs("data/processed/jsons/", exist_ok=True)

        json.dump(
            self.entries,
            open(f"data/processed/jsons/distill.json", "w"),
        )
        print(f"Finished updating {self.name}.json.")

        input("Fix any errors in the json and press enter to continue...")

        self.entries = json.load(open(f"data/processed/jsons/distill.json", "r"))

        print(
            f"Converting {self.name}.json to {self.name}.jsonl and {self.name}.txt..."
        )
        for k in self.entries.keys():
            yield self.entries[k]

    def fetch_individual_entries(self, html):
        soup = BeautifulSoup(html, "html.parser")
        title = soup.find("title").text
        # find anything with the property 'article:author'
        authors = soup.find_all("meta", {"property": "article:author"})
        # then for each author, get the content
        authors = [author.get("content") for author in authors]

        # same for dates
        date = soup.find("meta", {"property": "article:published"})
        # if content in date is not None, then get the content
        if date is not None:
            date_published = date.get("content")
        else:
            date_published = None

        # find the href with doi in it
        doi = soup.find_all("a", {"href": True})
        doi = [link.get("href") for link in doi if "doi" in link.get("href")]
        if len(doi) > 0:
            doi = doi[0]
        else:
            doi = None

        # the body is in the tag d-article
        body = soup.find("d-article")
        # the abstract is the first ptag in the body
        try:
            abstract = body.find("p").text.replace("\n", " ")
        except:
            abstract = ""
            pass

        md = MarkdownConverter()
        markdown_text = md.convert_soup(body)
        body = markdown_text

        # pull the ol with class references out of the soup
        references = soup.find("ol", {"class": "references"})
        if references:
            # for each reference li, get the the span with the class title
            references = [
                {"title": reference.find("span", {"class": "title"}).text}
                for reference in references.find_all("li")
            ]
            # walk through each li in the references ol, and if it has an a with href, add it to the dict
            for idx in range(len(references)):
                reference = references[idx]
                if reference.get("a") is not None:
                    reference["link"] = reference.get("a").get("href")
                references[idx] = reference
        else:
            references = None
        # build the json
        self.entries[self.i] = {
            "source": "distill",
            "source_type": "html",
            "converted_with": "python",
            "title": title,
            "authors": authors,
            "date_published": str(date_published),
            "abstract": abstract,
            "journal_ref": "distill-pub",
            "doi": doi,
            "text": body,
            "bibliography_bib": references,
        }

        self.i += 1

    def convert_distill_dir2jsonl_file(self, input_dir, output_file):
        self.i = 0
        with open(output_file, "w") as f:
            for file in os.listdir(input_dir):
                try:
                    if file.endswith(".html"):
                        with open(os.path.join(input_dir, file), "r") as f1:
                            html = f1.read()
                            paper_json = self.fetch_individual_entries(html)
                            f1.close()
                        f.write(f"{paper_json}\n")
                except:
                    print(f"Error processing {file}")
                    pass
                finally:
                    f1.close()
