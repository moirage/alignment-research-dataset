import feedparser
import os

from align_data.common import utils


class WordpressBlog:
    def __init__(self, url, strip=[], max_pages=2000):
        """
        url: URL of the blog
        strip: list of regexes to strip from the HTML
        max_pages: maximum number of RSS pages to fetch
        """
        self.blog_url = url
        self.feed_url = url + "/feed"
        self.cleaner = utils.HtmlCleaner(strip)
        self.max_pages = max_pages
        self.name = utils.url_to_filename(url)

    def fetch_entries(self):
        last_title = ""
        for page in range(0, self.max_pages):
            paged_url = "{}?paged={}".format(self.feed_url, page + 1)
            print("Fetching {} (max={})".format(paged_url, self.max_pages))
            d = feedparser.parse(paged_url)

            if (
                ("feed" not in d)
                or ("title" not in d["feed"])
                or (d["feed"]["title"] == last_title)
            ):
                print("Not a valid page. It looks like we've reached the end.")
                break
            last_title = d["feed"]["title"]

            for entry in d["entries"]:
                content_text = self.cleaner.clean(entry["content"][0]["value"])
                text = entry["title"] + "\n\n" + content_text
                entry["text"] = text
                entry["source"] = self.blog_url
                entry["source_type"] = "wordpress-blog"
                yield entry
