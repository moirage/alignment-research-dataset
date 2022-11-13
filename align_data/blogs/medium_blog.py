from dataclasses import dataclass
import requests
from bs4 import BeautifulSoup
import bs4
from align_data.common.alignment_dataset import AlignmentDataset, DataEntry
import logging
from urllib.parse import urljoin
from markdownify import markdownify
from tqdm import tqdm

logger = logging.getLogger(__name__)

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

    url: str
    done_key = "url"

    def setup(self):
        self._setup()

    def fetch_entries(self):
        self.setup()
        logger.info(f"Fetching entries from {self.url}")
        response = requests.get(self.url, allow_redirects=True)
        soup = BeautifulSoup(response.content, "html.parser")
        self.articles = soup.find_all("article")
        logger.info(f"Found {len(self.articles)} articles")

        for ii, article in enumerate(tqdm(self.articles)):


            title = article.find("h2")
            if title is None:
                continue
            title = title.contents[0]

            article_url = article.find_all("a")[0]["href"].split("?")[0]
            article_url = urljoin(self.url, article_url)

            if self._entry_done(article_url):
                # logger.info(f"Already done {article_url}")
                continue
            logger.info(f"Processing {ii}")


            text = self._get_article(article_url)

            new_entry = DataEntry({
                "source": self.url,
                "source_type": "medium_blog",
                "url": article_url,
                "title": self._to_text(title),
                "date_published": "n/a",
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
        return markdownify(article.content)