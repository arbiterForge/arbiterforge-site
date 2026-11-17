"""Receive the actual custom-domain app after Pages deployment, without credentials."""
import hashlib
import json
import re
import sys
import time
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen
from stage_sim import SITE, fetch, validate_html


def verify(site_commit, source_commit, digest):
    query = '?publication=' + site_commit
    receipt = json.loads(fetch(SITE + '/SIM/publication.json' + query, 20_000))
    if (receipt['site_commit'] != site_commit or receipt['source_commit'] != source_commit
            or receipt['html_sha256'] != digest):
        raise ValueError('Live publication receipt is stale or mismatched')
    html = fetch(SITE + '/SIM/' + query)
    validate_html(html, source_commit)
    if hashlib.sha256(html).hexdigest() != digest:
        raise ValueError('Live SIM differs from received upstream bytes')
    # GitHub Pages supplies the directory redirect; the app itself stays untouched.
    request = Request(SITE + '/SIM', headers={'User-Agent': 'ArbiterForge-SIM-Receiving/1.0'})
    with urlopen(request, timeout=30) as response:
        if response.status != 200 or response.geturl() != SITE + '/SIM/':
            raise ValueError('/SIM does not resolve to the actual /SIM/ app')
    print(f'LIVE VERIFIED: {SITE}/SIM/ source={source_commit} sha256={digest}')


if __name__ == '__main__':
    site, source, digest = sys.argv[1:4]
    if not re.fullmatch('[a-f0-9]{40}', site) or not re.fullmatch('[a-f0-9]{40}', source) or not re.fullmatch('[a-f0-9]{64}', digest):
        raise SystemExit('Expected exact site/source commits and HTML SHA-256')
    for attempt in range(12):
        try:
            verify(site, source, digest)
            break
        except (HTTPError, URLError, ValueError, KeyError, OSError) as error:
            print(f'Public receiving attempt {attempt + 1}/12: {error}', flush=True)
            if attempt == 11:
                raise
            time.sleep(10)
