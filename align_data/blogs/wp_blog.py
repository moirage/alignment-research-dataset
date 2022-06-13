import feedparser
import logging
import typing
from align_data import templates, utils


logger = logging.getLogger(__name__)


class WordpressBlog(templates.Dataset):

    def __init__(self, url, strip=[], max_pages=2000):
        """
        url: URL of the blog
        strip: list of regexes to strip from the HTML
        max_pages: maximum number of RSS pages to fetch
        """
        self.url = url + "/feed"
        self.cleaner = utils.HtmlCleaner(strip)
        self.max_pages = max_pages

    @property
    def name(self) -> str:
        return utils.url_to_filename(self.url)

    def fetch_entries(self) -> typing.Iterable[dict]:
        last_title = ""
        for page in range(0, self.max_pages):
            paged_url="{}?paged={}".format(self.url, page+1)

            logger.info("Fetching {} (max={})".format(paged_url, self.max_pages))
            d = feedparser.parse(paged_url)

            if ('feed' not in d) or ('title' not in d['feed']) or (d['feed']['title'] == last_title):
                logger.info("Not a valid page. It looks like we've reached the end.")
                break
            last_title = d["feed"]["title"]

            for entry in d["entries"]:
                content = entry["content"][0]["value"]
                text = entry["title"] + "\n\n" + self.cleaner.clean(content, False)
                yield {
                    "content": content,
                    "text": text,
                    "metadata": {
                        "article_url": entry["link"],
                        "title": entry["title"],
                    }
                }
