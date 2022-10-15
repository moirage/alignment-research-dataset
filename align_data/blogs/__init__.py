from .markdown_blogs import MarkdownBlogs
from .wp_blog import WordpressBlog
from .medium_blog import MediumBlog
from .gwern_blog import GwernBlog
from .other_blog import OtherBlog

BLOG_REGISTRY = [
    WordpressBlog(name = "aiimpacts.org",
                  url = "https://aiimpacts.org"),
    WordpressBlog(name = "aipulse.org",
                  url = "https://aipulse.org"),
    WordpressBlog(name = "aisafety.camp",
                  url = "https://aisafety.camp"),
    WordpressBlog(name = "intelligence.org",
                  url = "https://intelligence.org"),
    WordpressBlog(name = "jsteinhardt.wordpress.com",
                  url = "https://jsteinhardt.wordpress.com"),
    WordpressBlog(name = "qualiacomputing.com",
                  url = "https://qualiacomputing.com",
                  strip = ["^by [^\n].*\n"]),
    WordpressBlog(name = "vkrakovna.wordpress.com",
                  url = "https://vkrakovna.wordpress.com"),
    WordpressBlog(name = "www.yudkowsky.net",
                  url = "https://www.yudkowsky.net",
                  strip = ["^\s*Download as PDF\n"]),
    
    MediumBlog(name="deepmind.blog",
               url="https://deepmindsafetyresearch.medium.com/"),
    
    GwernBlog(name="gwern_blog"),
    
    OtherBlog(name="cold.takes",
              url="https://www.cold-takes.com/",
              class_name="u-permalink"),
              
    OtherBlog(name="generative.ink",
              url="https://generative.ink/posts/",
              class_name="post-title"),
    
    MarkdownBlogs(name="carado.moe",
                  gdrive_address="https://drive.google.com/uc?id=17CLAtrWNp4WoRLRPyS1pb2K5IQuMtHIH",
                  ),
    MarkdownBlogs(name="waitbutwhy",
                  gdrive_address="https://drive.google.com/uc?id=18T0LcYirruBW4c_fDQMEWAkA2KqSE1of",
                  ),
]
