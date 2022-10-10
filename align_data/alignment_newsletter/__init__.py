from .alignment_newsletter import AlignmentNewsletter
import os

ALIGNMENT_NEWSLETTER_REGISTRY = [
        AlignmentNewsletter( 
                name = "alignment_newsletter" , 
                newsletter_xlsx_path = os.path.join(os.path.abspath( os.path.dirname( __file__ ) ) , "../../tables/alignment_newsletter.xlsx")
        ),
]