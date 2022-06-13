from align_data.blogs.markdown_blogs import MarkdownBlogs
from align_data.ebooks.mdebooks import MDEBooks
from .wp_blog import WordpressBlog
from .medium_blog import MediumBlog
from .gwern_blog import GwernBlog
from .other_blog import OtherBlog


BLOG_REGISTRY = [
    WordpressBlog("https://aiimpacts.org"),
    WordpressBlog("https://aipulse.org"),
    WordpressBlog("https://aisafety.camp"),
    WordpressBlog("https://intelligence.org"),
    WordpressBlog("https://jsteinhardt.wordpress.com"),
    WordpressBlog("https://qualiacomputing.com", ["^by [^\n].*\n"]),
    WordpressBlog("https://vkrakovna.wordpress.com"),
    WordpressBlog("https://www.yudkowsky.net", ["^\s*Download as PDF\n"]),
    MediumBlog("https://deepmindsafetyresearch.medium.com/", "2018-09-27"),
    GwernBlog("https://www.gwern.net"),
    OtherBlog("https://www.cold-takes.com/", "u-permalink", False),
    OtherBlog("https://generative.ink/posts/", "post-title", False),
    MarkdownBlogs(
        "https://drive.google.com/uc?id=17CLAtrWNp4WoRLRPyS1pb2K5IQuMtHIH",
        "carado.moe",
        "carado.moe-cleaned-up",
    ),
    MarkdownBlogs(
        "https://drive.google.com/uc?id=18T0LcYirruBW4c_fDQMEWAkA2KqSE1of",
        "waitbutwhy.com",
        "waitbutwhy",
    ),
    MDEBooks(
        "https://drive.google.com/uc?id=1jRtk3LSa1cWxAYu0DO0VGFY-J710FCfB", "mdebooks"
    ),
]
