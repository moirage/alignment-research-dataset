import datetime
import dateutil.parser as dparser
import glob
import logging
import os
import requests
import re
import time
import typing
from bs4 import BeautifulSoup
from align_data import templates


logger = logging.getLogger(__name__)


class LessWrong(templates.Dataset):

    name = "lesswrong"

    def fetch_entries(self) -> typing.Iterable[dict]:
        logger.info("Grabbing most recent links (grabs all links if /urls/ is empty)...")
        self._get_all_links()
        logger.info("Converting each link to a json with post & comments...")
        logger.info("[Using only the latest urls, change variable url_directory in lesswrong.py to point at a specific url_folder]")
        # specify url_directory to the specific url_file you want
        for post in self._urls_to_json_scrape(file_prefix="lesswrong", url_directory=""):
            yield post

    def _get_latest_file(self):
        list_of_files = sorted(glob.glob("urls/*"))  # * means all if need specific format then *.csv
        return list_of_files[-1]

    def _url_to_soup(self, url):
        r = requests.get(url)
        html = r.content.decode('utf-8')
        return BeautifulSoup(html, 'html.parser')

    def _add_20_to_url(self, url):
        current_post_amount = re.findall(r'\d+', url)[0]
        url = url.replace(current_post_amount, str(int(current_post_amount) + 20))
        return url

    def _subtract_one_day(self, date):
        new_date = dparser.parse(date) - datetime.timedelta(1)
        return new_date.strftime("%Y-%m-%d")

    def _subtract_days(self, url):
        # find the first date
        both_dates = re.findall(r'\d+-\d+-\d+', url)
        # subtract day
        first_date = both_dates[0]
        new_date = self._subtract_one_day(first_date)
        # first replace the oldest date w/ one day before
        url = url.replace(first_date, new_date)
        # Then 2nd w/ first (equivalent to one day before 2nd)
        url = url.replace(both_dates[1], both_dates[0])
        return url

    def _get_all_links(self):
        today = datetime.datetime.today().strftime("%Y-%m-%d")
        url_for_today = "urls/" + today + "_links.txt"
        #check if there's a url_link for today, return if so
        if(os.path.isfile(url_for_today)):
            return

        #else grab most recent urls
        try:
            latest_file_name = self._get_latest_file()
            with open(latest_file_name) as previous_file:
                latest_url = previous_file.readline().rstrip()
        except:  # empty files
            latest_url = "n/a"

        with open(url_for_today, "w") as f:
            initial_url = "https://www.greaterwrong.com/index?view=all&offset=0"
            iterations = 0
            found_latest_url = False
            while not found_latest_url:
                iterations += 1
                if (iterations % 100 == 0):
                    logger.info("Currently: ", iterations)
                try:
                    # Find All Post Title tags for each page, then the url for the post
                    soup = self._url_to_soup(initial_url)
                    posts = soup.findAll(class_='post-title-link')
                    for linkParent in posts:
                        link = linkParent.get('href')
                        if link == latest_url:
                            found_latest_url = True
                            break
                        f.write(link + "\n")
                    initial_url = self._add_20_to_url(initial_url)
                    time.sleep(1)
                except Exception as e:
                    logger.warning(e)
                    logger.info("iterations: ", iterations)
                    logger.info("total files ~= ", iterations * 20)
                    break

    def _chunks(self, lst, n):
        """Yield successive n-sized chunks from lst."""
        for i in range(0, len(lst), n):
            yield lst[i:i + n]

    def _get_tag_warn(self, soup, separator="/"):
        tags_html = soup.find("div", {"id": "tags"})
        tag_list = []
        if tags_html:
            for tag in tags_html:
                tag_list.append(tag.text)
            return separator.join(tag_list)
        else:
            return ""

    def _cleanHtml(self, html):
        res = html
        res = re.sub("\u201c", '"', res)
        res = re.sub("\u201d", '"', res)
        # res = re.sub(r'http\S+', 'ʬ', res)
        return res

    def _latest_url_file_name(self, url_dir="urls"): 
        url_filenames = sorted(os.listdir(url_dir), reverse=True) # Do reverse to get latest date first
        return url_filenames[0]

    def _recursive_comment(self, comment):
        url = comment.select_one('.lw2-link').get("href")
        commentID_location = url.find("?commentId=") + len("?commentId=")
        id = url[commentID_location:]
        date = comment.select_one(".date").text.strip()
        date = datetime.datetime.strptime(date, '%d %b %Y %H:%M %Z').isoformat()[0:-3]
        username = comment.select_one('.author').text.strip()
        karma_temp = comment.select_one('.karma-value')
        karma_list = karma_temp.text.strip().split(" ")
        karma = karma_list[0]
        votes = karma_temp.get("title").split(" ")[0]
        text = self.add_consistent_newlines(comment.select_one('.body-text.comment-body').text.strip())

        json_comment = {
            "id": id,
            "author": username,
            "score": karma,
            "omega_karma": "",
            "votes": votes,
            "url": url,
            "date": date,
            "text": text,
            "comments": []
        }

        if len(karma_list) > 2:  # eg. LW: 420 AF: 69, list split by spaces
            json_comment["score"] = karma_list[1]
            json_comment["omega_karma"] = karma_list[3]

        # recursively apply to subcomments
        next_comment = comment.select_one(".comment-thread")
        if (next_comment):
            for sub_comment_parent in next_comment:
                if (len(sub_comment_parent.div.get("class")) > 1):
                    # print("deleted comment at: ", url, " w/ subcomment", sub_comment_parent)
                    continue
                try:
                    json_subcomment = self.recursive_comment(sub_comment_parent)
                    json_comment["comments"].append(json_subcomment)
                except:
                    pass
        return json_comment

    def _add_consistent_newlines(self, paragraph):
        # Add in Consistent Newlines
        paragraph = paragraph.replace("&newline", "\n")
        return paragraph

    def _encode_html_as_text(self, soup):
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
        #raw latex support
        for latex in soup.find_all("span", class_="mjx-math"):
            latex.string = ""
            latex.insert(0, latex.get("aria-label"))
        return  # insert is in-place, no need to return soup

    def _urls_to_json_scrape(self, file_prefix, url_directory=""):
        url_link_prefix_public_facing = "https://www.lesswrong.com"
        url_link_prefix = "https://www.greaterwrong.com"
        json_post_and_comments = []
        #get specific urls if specified
        if url_directory:
            url_filename_suffix = url_directory
        else: #get latest urls
            url_filename_suffix = self._latest_url_file_name(f"urls")
        #Create unproccessed_url directory if it doesn't exist already
        if not os.path.exists("unprocessed_urls"):
            os.makedirs("unprocessed_urls")
        # Run files in unprocessed if they exist (may contain problem files)
        unprocessed_urls = os.listdir(f"unprocessed_urls")
        if unprocessed_urls:  # if not empty
            url_filename_list = unprocessed_urls
        else:  # Create files to process
            url_filename = f"urls/{url_filename_suffix}"
            with open(url_filename, "r") as file:
                # Split into separate files for every 1000 urls
                lines = file.read().splitlines()
                list_of_url_by_1000 = list(self._chunks(lines, 1000))
                for index, urls_1000 in enumerate(list_of_url_by_1000):
                    with open(f"unprocessed_urls/{index}_{url_filename_suffix}", "w") as url_1000_file:
                        url_1000_file.writelines("\n".join(urls_1000))
            url_filename_list = os.listdir(f"unprocessed_urls")

        current_post_iter = 0
        for url_filename in url_filename_list:
            with open(f"unprocessed_urls/{url_filename}", "r") as file:
                for url_link in file:
                    # Show current iter post
                    if (current_post_iter % 50 == 0):
                        logger.info("current posts: ", current_post_iter)

                    full_url_link = url_link_prefix + url_link.rstrip('\n')
                    r = requests.get(full_url_link)
                    time.sleep(1)

                    html = r.content.decode('utf-8')
                    soup = BeautifulSoup(self._cleanHtml(html), 'html.parser')
                    # encode italics, bold, quotes, etc as text
                    self._encode_html_as_text(soup)

                    try:  # Check if missing url
                        post_title = self._add_consistent_newlines(
                            soup.select_one('.post-title').text.strip()[2:])  # Skip post_title Header_1
                        date = soup.select_one('.date').text.strip()
                        date = datetime.datetime.strptime(date, '%d %b %Y %H:%M %Z').isoformat()[0:-3]
                        author = soup.select_one('.author').text.strip()
                        karma_temp = soup.select_one('.karma-value')
                        post_votes = karma_temp.get("title").split(" ")[0]
                        karma_list = karma_temp.text.split(" ")
                        karma = karma_list[0]
                        post_content = self._add_consistent_newlines(soup.select_one('.body-text.post-body').text.strip())
                        tags = self.get_tag_list(soup, "/")
                    except:  # Event or missing url
                        logger.warning("Missing url at: ", full_url_link)
                        continue

                    # json object to save text in format
                    json_post_and_comments.append({
                        "id": full_url_link.split('/')[4],
                        "title": post_title,
                        "author": author,
                        "date": date,
                        "score": karma,
                        "omega_karma": "",
                        "votes": post_votes,
                        "tags": tags,
                        "url": url_link_prefix_public_facing + url_link.rstrip('\n'),
                        "text": post_content,
                        "source": file_prefix,  # "lesswrong" or "ea" atm
                        "comments": []
                    })

                    # check for alignment forum
                    if len(karma_list) > 2:  # eg. LW: 420 AF: 69, list split by spaces
                        json_post_and_comments[current_post_iter]["source"] = "alignment forum"
                        json_post_and_comments[current_post_iter]["score"] = karma_list[1]
                        json_post_and_comments[current_post_iter]["omega_karma"] = karma_list[3]
                    # Grab comments recursively
                    comments = soup.select_one('.comment-thread')
                    if comments:
                        for comment in comments:
                            if (len(comment.div.get("class")) > 1):
                                # print("deleted comment at: ", full_url_link, " w/ ", comment)
                                continue
                            try:
                                json_comment = self._recursive_comment(comment)
                                json_post_and_comments[current_post_iter]["comments"].append(json_comment)
                            except:
                                pass
                    # Update current post iter since we've actually added 1 post to the json
                    yield json_post_and_comments[current_post_iter]
                    current_post_iter += 1
            # remove url from unprocessed folder
            os.remove(f"unprocessed_urls/{url_filename}")


if __name__ == "__main__":
    lw = LessWrong()
    for post in lw.fetch_entries():
        print(post)
