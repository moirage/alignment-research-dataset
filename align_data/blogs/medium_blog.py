from dataclasses import dataclass
import requests
from bs4 import BeautifulSoup
import bs4
from align_data.common.alignment_dataset import AlignmentDataset , DataEntry
import logging
import sys
from urllib.parse import urljoin

logging.basicConfig(format='%(asctime)s | %(levelname)s : %(message)s',
                    level=logging.INFO, stream=sys.stdout)
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

@dataclass
class MediumBlog(AlignmentDataset):
    """
    Fetches articles from a Medium blog.

    Pulls Medium articles by walking the archive. Depending on the activity of the blog
    during a particular year, the archive for the year may consist of a single page only, or
    may have daily pages. A single blog can use different layouts for different years.

    Also, if the blog had few posts overall, an archive may not exist at all. In that case,
    the main page is used to fetch the articles. The entries are assumed to fit onto
    a single page, which seems to be the case for blogs without an archive.

    It is possible that there is additional variation in the layout that hasn't been represented
    in the blogs tested so far. In that case, additional fixes to this code may be needed.

    This implementation was originally based on
    https://dorianlazar.medium.com/scraping-medium-with-python-beautiful-soup-3314f898bbf5,
    but various fixes were added to handle a wider range of Medium blogs.
    """

    url : str

    def __post_init__(self):
        self.setup()
        logger.info(f"Fetching entries from {self.url}")
        response = requests.get(self.url, allow_redirects=True)
        soup = BeautifulSoup(response.content, "html.parser")
        self.articles = soup.find_all("article")
        logger.info(f"Found {len(self.articles)} articles")


    def fetch_entries(self):
        for ii , article in enumerate(self.articles):
            if self._entry_done(ii):
                logger.info(f"Already done {ii}")
                continue
            logger.info(f"Processing {ii}")
            
            title = article.find("h2")
            if title is None:
                continue
            title = title.contents[0]

            article_url = article.find_all("a")[0]["href"].split("?")[0]
            article_url = urljoin(self.url, article_url)

            text = self._get_article(article_url)

            new_entry = DataEntry({
                "source": self.url,
                "source_type": "medium_blog",
                "url": article_url,
                "title": self._to_text(title),
                "date_published" : "n/a",
                "text": text,
            })
            
            new_entry.add_id()

            yield new_entry
             
             
    def _to_text(self, s):
        if type(s) is bs4.element.Tag:
            return s.text
        return s
    
    def _get_article(self, url):
        logger.info("Fetching {}".format(url))
        article = requests.get(url, allow_redirects=True)
        article_soup = BeautifulSoup(article.text, "html.parser")

        sections = article_soup.find_all("section")
        blocks = []

        for section in sections:
            for block in section.find_all(["h1", "h2", "h3", "p"]):
                blocks.append(block.text)

        return "\n\n".join(blocks)