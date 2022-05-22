from .wp_blog import WordpressBlog
from .medium_blog import MediumBlog
from .gwern_blog import GwernBlog
from .other_blog import OtherBlog

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
    WordpressBlog("https://www.yudkowsky.net", ["^\s*Download as PDF\n"]),
    MediumBlog("https://ai-alignment.com", "2012-01-01"),
    MediumBlog("https://deepmindsafetyresearch.medium.com/", "2018-09-27"),
    MediumBlog("https://medium.com/@lucarade", "2018-04-28"),
    MediumBlog("https://medium.com/partnership-on-ai", "2020-04-15"),
    GwernBlog("https://www.gwern.net"),
    OtherBlog("https://www.cold-takes.com/" , "u-permalink" , False),
    OtherBlog("https://universalprior.substack.com/archive" , "post-preview-title" , True),
    OtherBlog("https://generative.ink/posts/" , "post-title" , False),
]
