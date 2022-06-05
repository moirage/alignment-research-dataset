import json
import sys
import subprocess
import shlex
import os


ARBITAL_SUBSPACES = [
    'ai_alignment',
    'math',
    'rationality',
]


def clean_page(page):
    return page


def get_page(alias, subspace, cache_dir):
    fn = os.path.join(cache_dir, f'arbital_{subspace}_{alias}.json')
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

        if not os.path.exists(cache_dir):
            os.makedirs(cache_dir, exist_ok=True)
        with open(fn, 'w') as f:
            f.write(json.dumps(data))

    p = data['pages'][alias]
    return clean_page({
        'alias': alias,
        'title': p['title'],
        'text': p['text'],
        'pageCreatedAt': p['pageCreatedAt'],
    })


def get_arbital_page_aliases(subspace, cache_dir):
    fn = os.path.join(cache_dir, f'arbital_{subspace}.json')
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
          -H 'referer: https://arbital.com/explore/{subspace}/' \\
          -H 'accept-language: en-US,en;q=0.9' \\
          --data-raw '{{"pageAlias":"{subspace}"}}' \\
          --compressed
        """
        cmd = shlex.split(cmd)
        out = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE).stdout
        data = json.loads(out)

        if not os.path.exists(cache_dir):
            os.makedirs(cache_dir, exist_ok=True)
        with open(fn, 'w') as f:
            f.write(json.dumps(data))

    return list(data['pages'].keys())