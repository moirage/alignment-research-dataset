import logging
import requests
import jsonlines

from align_data.common.alignment_dataset import AlignmentDataset, DataEntry
from dataclasses import dataclass
from tqdm import tqdm

logger = logging.getLogger(__name__)

@dataclass
class Arbital(AlignmentDataset):

    ARBITAL_SUBSPACES = ['ai_alignment', 'math', 'rationality']
    done_key = "alias"

    def setup(self):
        self._setup()

        self.headers = {
            'authority': 'arbital.com',
            'accept': 'application/json, text/plain, */*',
            'content-type': 'application/json;charset=UTF-8',
            'sec-ch-ua-mobile': '?0',
            'origin': 'https://arbital.com',
            'sec-fetch-site': 'same-origin',
            'sec-fetch-mode': 'cors',
            'sec-fetch-dest': 'empty',
            'accept-language': 'en-US,en;q=0.9',
        }

    def fetch_entries(self):
        self.setup()
        
        aliases = []
        for subspace in self.ARBITAL_SUBSPACES:
            aliases += self.get_arbital_page_aliases(subspace=subspace)

        for ii, alias in enumerate(tqdm(aliases)):
            if self._entry_done(alias):
                # logger.info(f"Already done {alias}")
                continue
            try:
                page = self.get_page(alias)
            except Exception as e:
                logger.error(f"Error getting page {alias}: {e}")
                page = {
                    'title': 'Error getting page',
                    'text': 'Error getting page',
                    'date_published': 'Error getting page',
                }
            new_entry = DataEntry({
                'title': page['title'] if 'title' in page else 'n/a',
                'text': page['text'] if 'text' in page else 'n/a',
                'date_published': page['pageCreatedAt'] if 'pageCreatedAt' in page else 'n/a',
                'url': 'n/a',
                'source': self.name,
                'source_filetype': 'text',
                'authors': 'n/a',
                'alias': alias,
            })
            new_entry.add_id()
            yield new_entry

    def get_arbital_page_aliases(self, subspace):
        headers = self.headers.copy()
        headers['referer'] = 'https://arbital.com/explore/{subspace}/'.format(
            subspace=subspace)
        data = '{{"pageAlias":"{subspace}"}}'.format(subspace=subspace)
        response = requests.post(
            'https://arbital.com/json/explore/', headers=headers, data=data).json()
        return list(response['pages'].keys())

    def get_page(self, alias):
        headers = self.headers.copy()
        headers['referer'] = 'https://arbital.com/'
        data = '{{"pageAlias":"{alias}"}}'.format(alias=alias)
        response = requests.post(
            'https://arbital.com/json/primaryPage/', headers=headers, data=data).json()
        return response['pages'][alias]
