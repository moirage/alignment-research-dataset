import logging
import requests
import typing
from align_data import templates, utils


logger = logging.getLogger(__name__)


class GwernBlog(templates.Dataset):
    """
    Fetches articles from a different blog by collecting links to articles
    from an index page.
    """

    def __init__(self, url):
        self.url = url
        self.cleaner = utils.HtmlCleaner()
        self.post_hrefs = [
            'https://www.gwern.net/Scaling-hypothesis.page',
            'https://www.gwern.net/Tanks.page',
            'https://www.gwern.net/Clippy.page',
            'https://www.gwern.net/Complexity-vs-AI.page',
            'https://www.gwern.net/Tool-AI.page',
            'https://www.gwern.net/Backstop.page',
            'https://www.gwern.net/Hyperbolic-Time-Chamber.page'
        ]

    @property
    def name(self) -> str:
        return utils.url_to_filename(self.url)

    def fetch_entries(self) -> typing.Iterable[dict]:
        for post_href in self.post_hrefs:
            content = self._get_article(post_href)
            text = self.cleaner.clean(content, False)
            yield {
                'content': content,
                'text': text,
                'metadata': {
                    'article_url': self.url,
                    # Parse Gwern `.page` title.
                    'title': text.split('---\ntitle:')[1].split('\n')[0].strip(),
                }
            }

    def _get_article(self, url):
        logger.info(f"Fetching {url}")
        article = requests.get(url, allow_redirects=True)
        return article.text
