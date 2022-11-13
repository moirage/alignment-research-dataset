from dataclasses import dataclass
import datetime
import dateutil.parser as dparser
import glob
import time
import requests
import re
import os
from bs4 import BeautifulSoup
import logging
from tqdm import tqdm
import sys

from align_data.common.alignment_dataset import AlignmentDataset , DataEntry

logger = logging.getLogger(__name__)
logging.basicConfig(stream=sys.stdout, level=logging.INFO)

@dataclass
class GreaterWrong(AlignmentDataset):

    """
    This class allows you to scrape posts and comments from GreaterWrong. 
    GreaterWrong contains all the posts from LessWrong (which contains the Alignment Forum) and the EA Forum.
    """

    COOLDOWN_TIME : int = 1
    done_key = "url"

    def setup(self):
        self._setup()
        self.output_dir = self.write_jsonl_path.parent / "raw" / self.name
        self.output_dir.mkdir_p()

    def fetch_entries(self):
        self.setup()
        logger.info(
            f"Grabbing most recent links (grabs all links if /{self.name}_urls/ is empty)...")
        self.get_all_links()
        logger.info("Converting each link to a json with post & comments...")
        logger.info(
            "[Using only the latest urls, change variable url_directory in greaterwrong.py to point at a specific url_folder]"
        )
        # specify url_directory to the specific url_file you want

        url_filename_list = self.get_urls(url_directory="")
        url_link_prefix_public_facing = "https://www.lesswrong.com" if self.name == "lesswrong" else "https://www.forum.effectivealtruism.org"
        
        ii = 0
        for url_filename in tqdm(url_filename_list):
            with open(self.output_dir / f"unprocessed_{self.name}_urls/{url_filename}", "r") as file:
                for url_link in tqdm(file):
                    if self._entry_done(url_link_prefix_public_facing
                + url_link.rstrip("\n")):
                        # logger.info(f"Already done {url_link}")
                        ii += 1
                        continue
                    post = self.get_url(self.name , url_link)
                    if post is None:
                        post = {
                            "text" : "n/a",
                            "url" : url_link_prefix_public_facing
                + url_link.rstrip("\n"),
                            "title" : "n/a",
                            "authors" : "n/a",
                            "date_published" : "n/a",
                            "source" : self.name
                        }
                    new_entry = DataEntry(post)
                    new_entry.add_id()
                    ii += 1
                    yield new_entry

    def get_latest_file(self):
        list_of_files = sorted(
            glob.glob( self.output_dir / f"{self.name}_urls/*")
        )  # * means all if need specific format then *.csv
        return list_of_files[-1]

    def url_to_soup(self, url):
        r = requests.get(url)
        html = r.content.decode("utf-8")
        return BeautifulSoup(html, "html.parser")

    def add_20_to_url(self, url):
        current_post_amount = re.findall(r"\d+", url)[0]
        url = url.replace(current_post_amount, str(
            int(current_post_amount) + 20))
        return url

    def subtract_one_day(self, date):
        new_date = dparser.parse(date) - datetime.timedelta(1)
        return new_date.strftime("%Y-%m-%d")

    def subtract_days(self, url):
        # find the first date
        both_dates = re.findall(r"\d+-\d+-\d+", url)
        # subtract day
        first_date = both_dates[0]
        new_date = self.subtract_one_day(first_date)
        # first replace the oldest date w/ one day before
        url = url.replace(first_date, new_date)
        # Then 2nd w/ first (equivalent to one day before 2nd)
        url = url.replace(both_dates[1], both_dates[0])
        return url

    def get_all_links(self):
        if not os.path.exists( self.output_dir / f"{self.name}_urls"):
            os.makedirs(self.output_dir / f"{self.name}_urls/")
        today = datetime.datetime.today().strftime("%Y-%m-%d")
        url_for_today = self.output_dir / f"{self.name}_urls/" + \
            today + "_links.txt"
        # check if there's a url_link for today, return if so
        if os.path.isfile(url_for_today):
            logger.info(f"Already have links for today: {today}")
            return

        # else grab most recent urls
        logger.info("Grabbing most recent links...")
        try:
            latest_file_name = self.get_latest_file()
            with open(latest_file_name) as previous_file:
                latest_url = previous_file.readline().rstrip()
        except:  # empty files
            logger.info("No previous files, starting from scratch...")
            latest_url = "n/a"

        with open(url_for_today, "w") as f:
            if self.name == "lesswrong":
                initial_url = "https://www.greaterwrong.com/index?view=all&offset=0"
            elif self.name == "eaforum":
                initial_url = "https://ea.greaterwrong.com/index?view=all&offset=0"
            iterations = 0
            found_latest_url = False
            while not found_latest_url:
                iterations += 1
                if iterations % 100 == 0:
                    logger.info(f"Currently: {iterations}")
                try:
                    # Find All Post Title tags for each page, then the url for the post
                    soup = self.url_to_soup(initial_url)
                    posts = soup.findAll(class_="post-title-link")
                    for linkParent in posts:
                        link = linkParent.get("href")
                        if link == latest_url:
                            found_latest_url = True
                            break
                        f.write(link + "\n")
                    initial_url = self.add_20_to_url(initial_url)
                    time.sleep(1)
                except Exception as e:
                    logger.info(e)
                    logger.info(f"iterations: {iterations}")
                    logger.info(f"total files ~= {iterations * 20}")
                    break

    def chunks(self, lst, n):
        """Yield successive n-sized chunks from lst."""
        for i in range(0, len(lst), n):
            yield lst[i: i + n]

    def get_tag_list(self, soup, separator="/"):
        tags_html = soup.find("div", {"id": "tags"})
        tag_list = []
        if tags_html:
            for tag in tags_html:
                tag_list.append(tag.text)
            return separator.join(tag_list)
        else:
            return ""

    def cleanHtml(self, html):
        res = html
        res = re.sub("\u201c", '"', res)
        res = re.sub("\u201d", '"', res)
        # res = re.sub(r'http\S+', 'ʬ', res)
        return res

    def latest_url_file_name(self, url_dir=""):
        url_filenames = sorted(
            os.listdir(url_dir), reverse=True
        )  # Do reverse to get latest date first
        return url_filenames[0]

    def recursive_comment(self, comment):
        url = comment.select_one(".lw2-link").get("href")
        commentID_location = url.find("?commentId=") + len("?commentId=")
        id = url[commentID_location:]
        date = comment.select_one(".date").text.strip()
        date = datetime.datetime.strptime(
            date, "%d %b %Y %H:%M %Z").isoformat()[0:-3]
        username = comment.select_one(".author").text.strip()
        karma_temp = comment.select_one(".karma-value")
        karma_list = karma_temp.text.strip().split(" ")
        karma = karma_list[0]
        votes = karma_temp.get("title").split(" ")[0]
        text = self.add_consistent_newlines(
            comment.select_one(".body-text.comment-body").text.strip()
        )

        json_comment = {
            "id": id,
            "authors": username,
            "score": karma,
            "omega_karma": "",
            "votes": votes,
            "url": url,
            "date_published": date,
            "text": text,
            "comments": [],
        }

        if len(karma_list) > 2:  # eg. LW: 420 AF: 69, list split by spaces
            json_comment["score"] = karma_list[1]
            if self.name == "lesswrong":
                json_comment["omega_karma"] = karma_list[3]

        # recursively apply to subcomments
        next_comment = comment.select_one(".comment-thread")
        if next_comment:
            for sub_comment_parent in next_comment:
                if len(sub_comment_parent.div.get("class")) > 1:
                    # print("deleted comment at: ", url, " w/ subcomment", sub_comment_parent)
                    continue
                try:
                    json_subcomment = self.recursive_comment(
                        sub_comment_parent)
                    json_comment["comments"].append(json_subcomment)
                except:
                    pass
        return json_comment

    def add_consistent_newlines(self, paragraph):
        # Add in Consistent Newlines
        paragraph = paragraph.replace("&newline", "\n")
        return paragraph

    def encode_html_as_text(self, soup):
        # Convert different tags into text we would want GPT to learn
        # for a in soup.select('a'):
        #     a.insert(len(a), " ʬ")
        for li in soup.select("li"):
            li.insert(0, "&newline - ")
        for blockquote in soup.select("blockquote"):
            for child in blockquote.children:
                c = child
                if c.name != None:
                    break
            try:
                c.insert(0, "> ")
            except:  # Has no nested children tags, just insert first
                blockquote.insert(0, "> ")
        for italics in soup.select("em"):
            italics.insert(len(italics), "*")
            italics.insert(0, "*")
        for italics in soup.select("i"):
            italics.insert(len(italics), "*")
            italics.insert(0, "*")
        for paragraphs in soup.select("p"):
            paragraphs.insert(len(paragraphs), "&newline")
        for headings in soup.select("h1"):
            headings.insert(len(headings), "&newline")
            headings.insert(0, "# ")
        for headings in soup.select("h2"):
            headings.insert(len(headings), "&newline")
            headings.insert(0, "## ")
        for headings in soup.select("h3"):
            headings.insert(len(headings), "&newline")
            headings.insert(0, "### ")
        for nav in soup.select("nav"):
            nav.insert(len(nav), "&newline")
        for bold in soup.select("b"):
            bold.insert(len(bold), "**")
            bold.insert(0, "**")
        for bold in soup.select("strong"):
            bold.insert(len(bold), "**")
            bold.insert(0, "**")
        # raw latex support
        for latex in soup.find_all("span", class_="mjx-math"):
            latex.string = ""
            latex.insert(0, latex.get("aria-label"))
        return  # insert is in-place, no need to return soup

    def get_urls(self, url_directory=""):
        # get specific urls if specified
        if url_directory:
            url_filename_suffix = url_directory
        else:  # get latest urls
            url_filename_suffix = self.latest_url_file_name(
                self.output_dir / f"{self.name}_urls")
        # Create unproccessed_url directory if it doesn't exist already
        if not os.path.exists(self.output_dir / f"unprocessed_{self.name}_urls"):
            os.makedirs(
                self.output_dir / f"unprocessed_{self.name}_urls")
        # Run files in unprocessed if they exist (may contain problem files)
        unprocessed_urls = os.listdir(
            self.output_dir / f"unprocessed_{self.name}_urls")
        if unprocessed_urls:  # if not empty
            url_filename_list = unprocessed_urls
        else:  # Create files to process
            url_filename = self.output_dir / f"{self.name}_urls/{url_filename_suffix}"
            with open(url_filename, "r") as file:
                # Split into separate files for every 1000 urls
                lines = file.read().splitlines()
                list_of_url_by_1000 = list(self.chunks(lines, 1000))
                for index, urls_1000 in enumerate(list_of_url_by_1000):
                    with open(
                        self.output_dir / f"unprocessed_{self.name}_urls/{index}_{url_filename_suffix}", "w"
                    ) as url_1000_file:
                        url_1000_file.writelines("\n".join(urls_1000))
            url_filename_list = os.listdir(
                self.output_dir / f"unprocessed_{self.name}_urls")
        return url_filename_list

    def get_url(self, file_prefix , url_link):
        if self.name == "lesswrong":
            url_link_prefix_public_facing = "https://www.lesswrong.com"
            url_link_prefix = "https://www.greaterwrong.com"
        elif self.name == "eaforum":
            url_link_prefix_public_facing = "https://www.forum.effectivealtruism.org"
            url_link_prefix = "https://ea.greaterwrong.com"
        
        full_url_link = url_link_prefix + url_link.rstrip("\n")
        r = requests.get(full_url_link)
        time.sleep(self.COOLDOWN_TIME)

        html = r.content.decode("utf-8")
        soup = BeautifulSoup(self.cleanHtml(html), "html.parser")

        # encode italics, bold, quotes, etc as text
        self.encode_html_as_text(soup)

        try:  # Check if missing url
            post_title = self.add_consistent_newlines(
                soup.select_one(".post-title").text.strip()[2:]
            )  # Skip post_title Header_1
            date = soup.select_one(".date").text.strip()
            date = datetime.datetime.strptime(
                date, "%d %b %Y %H:%M %Z"
            ).isoformat()[0:-3]
            author = soup.select_one(".author").text.strip()
            karma_temp = soup.select_one(".karma-value")
            post_votes = karma_temp.get("title").split(" ")[0]
            karma_list = karma_temp.text.split(" ")
            karma = karma_list[0]
            post_content = self.add_consistent_newlines(
                soup.select_one(
                    ".body-text.post-body").text.strip()
            )
            tags = self.get_tag_list(soup, "/")
        except Exception as e:  # Event or missing url
            logger.error(f"Error: {e}")
            logger.info(f"Missing url at: {full_url_link}")
            return None

        # json object to save text in format
        json_post_and_comment = {
                # "id": full_url_link.split("/")[4],
                "title": post_title,
                "authors": author,
                "date_published": date,
                "score": karma,
                "omega_karma": "",
                "votes": post_votes,
                "tags": tags,
                "url": url_link_prefix_public_facing
                + url_link.rstrip("\n"),
                "text": post_content,
                "source": file_prefix,  # "lesswrong" or "ea" atm
                "comments": [],
            }

        # check for alignment forum
        if len(karma_list) > 2:  # eg. LW: 420 AF: 69, list split by spaces
            if self.name == "lesswrong":
                json_post_and_comment[
                    "source"
                ] = "alignment forum"
                json_post_and_comment["score"] = karma_list[
                    1
                ]
                json_post_and_comment[
                    "omega_karma"
                ] = karma_list[3]
            elif self.name == "eaforum":
                json_post_and_comment[
                    "source"
                ] = "eaforum"
                json_post_and_comment["score"] = karma_list[
                    1
                ]
        # Grab comments recursively
        comments = soup.select_one(".comment-thread")
        if comments:
            for comment in comments:
                if len(comment.div.get("class")) > 1:
                    # print("deleted comment at: ", full_url_link, " w/ ", comment)
                    continue
                try:
                    json_comment = self.recursive_comment(comment)
                    json_post_and_comment[
                        "comments"
                    ].append(json_comment)
                except Exception as e:
                    logger.error(f"Error: {e}")
                    logger.info(f"Missing comment at: {full_url_link}")
                    pass
        # Update current post iter since we've actually added 1 post to the json
        return json_post_and_comment
