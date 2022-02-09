import bs4
import requests

from bs4 import BeautifulSoup
from datetime import datetime
from dateutil.relativedelta import relativedelta
from urllib.parse import urljoin

from . import utils

class MediumBlog:
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

    def __init__(self, url, start_date_str):
        self.url = url
        self.start_date = datetime.strptime(start_date_str, "%Y-%m-%d")

        self.cleaner = utils.HtmlCleaner("Other articles you may find interesting:[.\n]*")
        self.name = utils.url_to_filename(url)

        self.is_first = True

    def fetch_entries(self):
        if self._archive_exists():
            print("Archive exists. Fetching entries from the archive.")
            return self._fetch_entries_from_archive()
        else:
            # Note: we are assuming that paging is not necessary in this case.
            # We haven't yet seen an example of a medium blog where this is not the case.
            print("Archive does not exist. Fetching entries from the main page only.")
            response = requests.get(self.url, allow_redirects=True)
            return self._get_entries_from_main(response)

    def _archive_exists(self):
        archive_url = "{}/archive".format(self.url)
        response = requests.get(archive_url, allow_redirects=False)
        if response.status_code != 200 and response.status_code != 404:
            print("WARNING: Unexpected status code {} for {} (probing archive existence)".format(response.status_code, archive_url))
        return response.status_code == 200

    def _fetch_entries_from_archive(self):
        d = self.start_date
        now = datetime.now()

        while d < now:
            entries, delta = self._fetch_entries_from_date(d.year, d.month, d.day)
            for entry in entries:
                yield entry

            d = d + delta

    def _fetch_entries_from_date(self, year, month, day):
        day_url = "{0}/archive/{1}/{2:02d}/{3:02d}".format(self.url, year, month, day)
        year_url = "{}/archive/{}".format(self.url, year)

        print("Fetching {}".format(day_url))
        response = requests.get(day_url, allow_redirects=True)
        if response.url.startswith(day_url):
            # There are posts for this day. Fetch them and advance a day.
            return self._get_entries_from_archive(response), relativedelta(days=1)
        elif response.url.startswith(year_url):
            # There are posts this year, but there are no daily pages. Fetch the posts and advance a year.
            return self._get_entries_from_archive(response), relativedelta(years=1)
        else:
            # No posts this year. Advance a year.
            return [], relativedelta(years=1)

    def _get_entries_from_archive(self, response):
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

    def _get_entries_from_main(self, response):
        soup = BeautifulSoup(response.content, 'html.parser')
        articles = soup.find_all("article")

        for article in articles:
            if self.is_first:
                self.is_first = False
            else:
                utils.random_delay()

            title = article.find("h2")
            if title is None:
                continue
            title = title.contents[0]

            article_url = article.find_all("a")[0]['href'].split('?')[0]
            article_url = urljoin(self.url, article_url)

            content = self._get_article(article_url)
            text = self.cleaner.clean(content)

            yield {
                "article_url": article_url,
                "title": self._to_text(title),
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
