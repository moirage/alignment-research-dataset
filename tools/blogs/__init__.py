from pprint import pprint

from .wp_blog import WordpressBlog

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
]

ALL_BLOGS = sorted([blog.name for blog in BLOG_REGISTRY])
BLOG_MAP = dict([(blog.name, blog) for blog in BLOG_REGISTRY])

def get_blog(blog_name):
    try:
        return BLOG_MAP[blog_name]
    except KeyError as e:
        print("Available blogs:")
        pprint(ALL_BLOGS)
        raise KeyError(f"Missing blog {blog_name}")
