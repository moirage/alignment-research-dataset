import requests
import time
import re

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager

from bs4 import BeautifulSoup
from datetime import datetime
from dateutil.relativedelta import relativedelta
from urllib.parse import urljoin

from align_data.common import utils


class OtherBlog:
    """
    Fetches articles from a different blog by collecting links to articles from an index page.

    """

    def __init__(self, url, class_name, do_scroll=True):
        self.url = url
        self.class_name = class_name
        self.do_scroll = do_scroll
        self.cleaner = utils.HtmlCleaner(
            ["You might also like\.\.\..*", "\\n+", "\#\# Create your profile.*"],
            ["", "\\n", ""],
            True,
        )
        self.name = utils.url_to_filename(url)

        self.is_first = True

    def fetch_entries(self):
        post_hrefs = self._selenium_get_post_hrefs(
            self.url, self.class_name, self.do_scroll
        )
        for post_href in post_hrefs:
            content = self._get_article(post_href)
            text = self.cleaner.clean(content, True)
            yield {"text": text, "url": self.url, "title": text.split("\n")[0]}

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
        browser.get(index_page)
        time.sleep(DELAY_GET)

        elem = browser.find_element_by_tag_name(tag_name)
        if do_scroll:
            [
                elem.send_keys(Keys.PAGE_DOWN) and time.sleep(SCROLL_SLEEP)
                for _ in range(NO_OF_PAGEDOWN)
            ]

        time.sleep(DELAY_GET)

        post_elems = browser.find_elements_by_class_name(class_name)
        post_hrefs = [post.get_attribute("href") for post in post_elems]
        if post_hrefs[0] is None:
            post_hrefs = [
                browser.find_element_by_link_text(post.text).get_attribute("href")
                for post in post_elems
            ]
        browser.close()

        return post_hrefs

    def _get_article(self, url):
        print("Fetching {}".format(url))
        article = requests.get(url, allow_redirects=True)

        return article.text
