import json
import sys
import subprocess
import shlex
import os

# is there a place for cached files yet?
DATA_DIR = 'data/arbital'


def get_page(alias):
    fn = os.path.join(DATA_DIR, f'arbital_{alias}.json')
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
        out = subprocess.run(cmd, stdout=subprocess.PIPE).stdout
        data = json.loads(out)

        if not os.path.exists(DATA_DIR):
            os.makedirs(DATA_DIR, exist_ok=True)
        with open(fn, 'w') as f:
            f.write(json.dumps(data))

    p = data['pages'][alias]
    return {
        'title': p['title'],
        'text': p['text'],
        'pageCreatedAt': p['pageCreatedAt'],
    }


def get_arbital_page_aliases():
    fn = os.path.join(DATA_DIR, f'arbital.json')
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
          -H 'referer: https://arbital.com/explore/ai_alignment/' \\
          -H 'accept-language: en-US,en;q=0.9' \\
          --data-raw '{{"pageAlias":"ai_alignment"}}' \\
          --compressed
        """
        cmd = shlex.split(cmd)
        out = subprocess.run(cmd, stdout=subprocess.PIPE).stdout
        data = json.loads(out)

        if not os.path.exists(DATA_DIR):
            os.makedirs(DATA_DIR, exist_ok=True)
        with open(fn, 'w') as f:
            f.write(json.dumps(data))

    return list(data['pages'].keys())


def iter_pages():
    for alias in tqdm(get_arbital_page_aliases()):
        yield get_page(alias)

