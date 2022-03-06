from pprint import pprint

from .wp_blog import WordpressBlog
from .medium_blog import MediumBlog

BLOG_REGISTRY = [
    WordpressBlog("https://aiimpacts.org"),
    WordpressBlog("https://aipulse.org"),
    WordpressBlog("https://aisafety.camp"),
    WordpressBlog("https://casparoesterheld.com"),
    WordpressBlog("https://futureoflife.org"),
    WordpressBlog("https://intelligence.org"),
    WordpressBlog("https://jsteinhardt.wordpress.com"),
    WordpressBlog("https://longtermrisk.org/blog"),
    WordpressBlog("https://qualiacomputing.com", ["^by [^\n].*\n"]),
    WordpressBlog("https://slatestarcodex.com"),
    WordpressBlog("https://unstableontology.com"),
    WordpressBlog("https://vkrakovna.wordpress.com"),
    WordpressBlog("https://www.econlib.org"),
    WordpressBlog("https://www.ibm.com/blogs/policy"),
    WordpressBlog("https://www.microsoft.com/en-us/research/blog"),
    WordpressBlog("https://www.yudkowsky.net", ["^\s*Download as PDF\n"]),
    MediumBlog("https://ai-alignment.com", "2012-01-01"),
    MediumBlog("https://towardsdatascience.com", "2010-11-21"),
    MediumBlog("https://deepmindsafetyresearch.medium.com/", "2018-09-27"),
    MediumBlog("https://medium.com/@lucarade", "2018-04-28"),
    MediumBlog("https://medium.com/partnership-on-ai", "2020-04-15"),
]

