import requests
from bs4 import BeautifulSoup
from datetime import datetime
from dateutil.relativedelta import relativedelta

from . import utils

class MediumBlog:
    """
    Fetches articles from a Medium blog.

    Pulls Medium articles by walking the archive. Depending on the activity of the blog
    during a particular year, the archive for the year may consist of a single page only, or
    may have daily pages. A single blog can use different layouts for different years.

    It is possible that there is additional variation in the layout that hasn't been represented
    in the blogs tested so far. In that case, additional fixes to this code may be needed.

    This implementation is loosely based on on
    https://dorianlazar.medium.com/scraping-medium-with-python-beautiful-soup-3314f898bbf5,
    but with additional fixes.
    """

    def __init__(self, url, start_date_str):
        self.url = url
        self.start_date = datetime.strptime(start_date_str, "%Y-%m-%d")

        self.cleaner = utils.HtmlCleaner("Other articles you may find interesting:[.\n]*")
        self.name = utils.url_to_filename(url)

        self.is_first = True

    def fetch_entries(self):
        d = self.start_date
        now = datetime.now()

        while d < now:
            entries, delta = self._fetch_entries_from(d.year, d.month, d.day)
            for entry in entries:
                yield entry

            d = d + delta

    def _fetch_entries_from(self, year, month, day):
        day_url = "{0}/archive/{1}/{2:02d}/{3:02d}".format(self.url, year, month, day)
        year_url = "{}/archive/{}".format(self.url, year)

        print("Fetching {}".format(day_url))
        response = requests.get(day_url, allow_redirects=True)
        if response.url.startswith(day_url):
            # There are posts for this day. Fetch them and advance a day.
            return self._get_entries(response), relativedelta(days=1)
        elif response.url.startswith(year_url):
            # There are posts this year, but there are no daily pages. Fetch the posts and advance a year.
            return self._get_entries(response), relativedelta(years=1)
        else:
            # No posts this year. Advance a year.
            return [], relativedelta(years=1)
    
    def _get_entries(self, response):
        soup = BeautifulSoup(response.content, 'html.parser')
        articles = soup.find_all("div", class_="postArticle postArticle--short js-postArticle js-trackPostPresentation js-trackPostScrolls")

        for article in articles:
            if self.is_first:
                self.is_first = False
            else:
                utils.random_delay()

            title = article.find("h3", class_="graf--title")
            if title is None:
                continue
            title = title.contents[0]
            subtitle = article.find("h4", class_="graf--subtitle")
            subtitle = subtitle.contents[0] if subtitle is not None else ''
            article_url = article.find_all("a")[3]['href'].split('?')[0]

            content = self._get_article(article_url)
            text = self.cleaner.clean(content)

            yield {
                "article_url": article_url,
                "title": self._to_text(title),
                "subtitle": self._to_text(subtitle),
                "content": content,
                "text": text,
            }

    def _get_article(self, url):
        print("Fetching {}".format(url))
        article = requests.get(url, allow_redirects=True)
        article_soup = BeautifulSoup(article.text, 'html.parser')

        sections = article_soup.find_all('section')
        blocks = []

        for section in sections:
            for block in section.find_all(['h1', 'h2', 'h3', 'p']):
                blocks.append(block.text)

        return "\n\n".join(blocks)

    def _to_text(self, s):
        if type(s) is bs4.element.Tag:
            return s.text
        return s
