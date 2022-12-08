from .gdocs import Gdocs

# 2022-06-01: Current iteration only include "AI Researcher Interviews"
# from https://www.lesswrong.com/posts/LfHWhcfK92qh2nwku/transcripts-of-interviews-with-ai-researchers

GDOCS_REGISTRY = [
    Gdocs(name = "gdocs",
        gdrive_address = "https://drive.google.com/uc?id=1gZc-z8kc_rdbIuInw8lqoA8cas2IpDLJ")
]
