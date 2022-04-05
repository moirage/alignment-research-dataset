import requests
from align_data.common import utils

class GwernBlog:
    """
    Fetches articles from a different blog by collecting links to articles from an index page.

    """

    def __init__(self, url):
        self.url = url
        self.cleaner = utils.HtmlCleaner()
        self.name = utils.url_to_filename(url)
        self.post_hrefs = ['https://www.gwern.net/Scaling-hypothesis.page','https://www.gwern.net/Tanks.page','https://www.gwern.net/Clippy.page','https://www.gwern.net/Complexity-vs-AI.page','https://www.gwern.net/Tool-AI.page','https://www.gwern.net/Backstop.page','https://www.gwern.net/Hyperbolic-Time-Chamber.page']



    def fetch_entries(self):
        for post_href in self.post_hrefs:
            content = self._get_article(post_href)
            text = self.cleaner.clean(content,False)
            yield {'text':text,"article_url": self.url,"title": text.split('\n')[0]}

    def _get_article(self, url):
        print("Fetching {}".format(url))
        article = requests.get(url, allow_redirects=True)
        
        return article.text
