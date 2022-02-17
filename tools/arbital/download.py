import json
import sys
import subprocess
import shlex
import os


def get_page(alias, subset, data_dir):
    fn = os.path.join(data_dir, f'arbital_{subset}_{alias}.json')
    if os.path.exists(fn):
        with open(fn, 'r') as f:
            data = json.load(f)
    else:

        cmd = f"""curl "https://arbital.com/json/primaryPage/" \\
          -H 'authority: arbital.com' \\
          -H 'accept: application/json, text/plain, */*' \\
          -H 'content-type: application/json;charset=UTF-8' \\
          -H 'sec-ch-ua-mobile: ?0' \\
          -H 'origin: https://arbital.com' \\
          -H 'sec-fetch-site: same-origin' \\
          -H 'sec-fetch-mode: cors' \\
          -H 'sec-fetch-dest: empty' \\
          -H 'referer: https://arbital.com/' \\
          -H 'accept-language: en-US,en;q=0.9' \\
          --data-raw '{{"pageAlias":"{alias}"}}' \\
          --compressed
        """
        cmd = shlex.split(cmd)
        out = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE).stdout
        data = json.loads(out)

        if not os.path.exists(data_dir):
            os.makedirs(data_dir, exist_ok=True)
        with open(fn, 'w') as f:
            f.write(json.dumps(data))

    p = data['pages'][alias]
    return {
        'title': p['title'],
        'text': p['text'],
        'pageCreatedAt': p['pageCreatedAt'],
    }


def get_arbital_page_aliases(subset, data_dir):
    fn = os.path.join(data_dir, f'arbital_{subset}.json')
    if os.path.exists(fn):
        with open(fn, 'r') as f:
            data = json.load(f)
    else:

        cmd = f"""curl 'https://arbital.com/json/explore/' \\
          -H 'authority: arbital.com' \\
          -H 'accept: application/json, text/plain, */*' \\
          -H 'content-type: application/json;charset=UTF-8' \\
          -H 'sec-ch-ua-mobile: ?0' \\
          -H 'origin: https://arbital.com' \\
          -H 'sec-fetch-site: same-origin' \\
          -H 'sec-fetch-mode: cors' \\
          -H 'sec-fetch-dest: empty' \\
          -H 'referer: https://arbital.com/explore/{subset}/' \\
          -H 'accept-language: en-US,en;q=0.9' \\
          --data-raw '{{"pageAlias":"{subset}"}}' \\
          --compressed
        """
        cmd = shlex.split(cmd)
        out = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE).stdout
        data = json.loads(out)

        if not os.path.exists(data_dir):
            os.makedirs(data_dir, exist_ok=True)
        with open(fn, 'w') as f:
            f.write(json.dumps(data))

    return list(data['pages'].keys())


def iter_arbital_pages(subset='ai_alignment', data_dir='data/arbital', progress=True):
    """
    Returns a yields pages found on the arbital website, caching them into `data_dir`.
    The subset must be 'ai_alignment', 'math', or 'rationality'.
    Each page has the following attributes:

        {
            'title': str,  # title of the article
            'text': str,  # text contents of the article
            'pageCreatedAt': str,  # ISO formatted date string
        }

    """

    assert subset in ['ai_alignment', 'math', 'rationality']

    if progress:
        from tqdm import tqdm
    else:
        def tqdm(a):
            return a

    for alias in tqdm(get_arbital_page_aliases(subset, data_dir)):
        yield get_page(alias, subset, data_dir)


for page in iter_arbital_pages(subset='math'):
    pass
    #print(page['title'])

