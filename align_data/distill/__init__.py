from .distill import Distill
import os

DISTILL_REGISTRY = [
    Distill(
        name = "distill",
        DISTILL_POSTS_DIR = os.path.join(os.path.abspath( os.path.dirname( __file__ ) ) , "../../align_data/distill/distill_posts/")
    ),
]
