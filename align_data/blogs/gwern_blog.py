from dataclasses import dataclass
import requests
from align_data.common.alignment_dataset import AlignmentDataset, DataEntry
import logging
import time
from tqdm import tqdm 

logger = logging.getLogger(__name__)


@dataclass
class GwernBlog(AlignmentDataset):
    """
    Fetches articles from a different blog by collecting links to articles from an index page.
    """

    COOLDOWN: int = 1
    done_key = "url"

    def setup(self):
        self._setup()
        self.post_hrefs = ['https://www.gwern.net/Scaling-hypothesis.page',
                           'https://www.gwern.net/Tanks.page',
                           'https://www.gwern.net/Clippy.page',
                           'https://www.gwern.net/Complexity-vs-AI.page',
                           'https://www.gwern.net/Tool-AI.page',
                           'https://www.gwern.net/Backstop.page',
                           'https://www.gwern.net/Hyperbolic-Time-Chamber.page']

    def fetch_entries(self):
        self.setup()
        for ii, post_href in enumerate(tqdm(self.post_hrefs)):
            if self._entry_done(post_href):
                # logger.info(f"Already done {post_href}")
                continue
            text = self._get_article(post_href)

            new_entry = DataEntry({
                "source": "gwern",
                "url": post_href,
                "title": text.splitlines()[1].split("title: ")[1],
                "authors": "Gwern Branwen",
                "date_published": "n/a",
                "text": text,
            })

            new_entry.add_id()

            # {'text':text,"article_url": self.url,"title": text.split('\n')[0]}
            yield new_entry

            time.sleep(self.COOLDOWN)

    def _get_article(self, url):
        logger.info("Fetching {}".format(url))
        article = requests.get(url, allow_redirects=True)
        return article.text
