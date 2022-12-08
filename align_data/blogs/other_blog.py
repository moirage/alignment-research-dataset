from dataclasses import dataclass
import requests
import time
import logging

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager
from markdownify import markdownify
from tqdm import tqdm
from selenium.webdriver.common.by import By

from align_data.common import utils
from align_data.common.alignment_dataset import AlignmentDataset, DataEntry

logger = logging.getLogger(__name__)

@dataclass
class OtherBlog(AlignmentDataset):
    """
    Fetches articles from a different blog by collecting links to articles from an index page.
    """

    url: str
    class_name: str
    done_key = "url"

    def setup(self):
        self._setup()
        self.cleaner = utils.HtmlCleaner(
            ["You might also like\.\.\..*", "\\n+", "\#\# Create your profile.*"],
            ["", "\\n", ""],
            True,
        )

    def fetch_entries(self):
        self.setup()
        post_hrefs = self._selenium_get_post_hrefs(
            self.url, self.class_name, True
        )
        for ii, post_href in enumerate(tqdm(post_hrefs)):
            if self._entry_done(post_href):
                # logger.info(f"Already done {post_href}")
                continue
            content = self._get_article(post_href)
            text = self.cleaner.clean(content, True)

            new_entry = DataEntry({
                "text": text,
                "url": post_href,
                "title": text.split("\n")[0],
                "source": self.name,
                "date_published": "n/a",
            })
            new_entry.add_id()
            yield new_entry

    def _selenium_get_post_hrefs(
        self,
        index_page,
        class_name,
        do_scroll=True,
        tag_name="body",
        DELAY_GET=1,
        NO_OF_PAGEDOWN=20,
        SCROLL_SLEEP=0.2,
    ):

        browser = webdriver.Chrome(ChromeDriverManager().install())
        browser.implicitly_wait(2) # gives an implicit wait for 20 seconds

        browser.get(index_page)
        time.sleep(DELAY_GET)

        elem = browser.find_element(By.TAG_NAME , tag_name)

        if do_scroll:
            [
                elem.send_keys(Keys.PAGE_DOWN) and time.sleep(SCROLL_SLEEP)
                for _ in range(NO_OF_PAGEDOWN)
            ]

        time.sleep(DELAY_GET)

        post_elems = browser.find_elements(By.CLASS_NAME, class_name)
        post_hrefs = [post.get_attribute("href") for post in post_elems]
        if post_hrefs[0] is None:
            post_hrefs = [
                browser.find_element(By.LINK_TEXT,
                    post.text).get_attribute("href")
                for post in post_elems
            ]
        browser.close()

        return post_hrefs

    def _get_article(self, url):
        logger.info("Fetching {}".format(url))
        article = requests.get(url, allow_redirects=True)

        return markdownify(article.content)
