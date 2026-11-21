"""Verify the deployed domain path and every publicly served stage asset."""
import json
from itertools import count
import re
import sys
import time
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from stage_meridian import MAX_MANIFEST, SITE, digest, fetch, manifest_entries, receive_assets
from stage_meridian_aliases import ALIAS_HTML

# GitHub Pages serves a ten-minute max-age for the public entry and manifest.
RECEIVE_WINDOW_SECONDS = 12 * 60
RETRY_INTERVAL_SECONDS = 15


def verify(site_commit, source_commit, expected_digest):
    origin = SITE + '/Meridian/'
    # The site commit can stay fixed across many Meridian publications.
    query = f'?publication={site_commit}&source={source_commit}&check={time.time_ns()}'
    receipt = json.loads(fetch(origin + 'publication.json' + query, 20_000))
    if (receipt['site_commit'] != site_commit or receipt['source_commit'] != source_commit
            or receipt['manifest_sha256'] != expected_digest):
        raise ValueError('Live Meridian publication receipt is stale or mismatched')
    raw = fetch(origin + 'build.json' + query, MAX_MANIFEST)
    if digest(raw) != expected_digest:
        raise ValueError('Live Meridian manifest differs from received upstream bytes')
    assets = receive_assets(origin, manifest_entries(json.loads(raw), source_commit), query)
    request = Request(origin.rstrip('/'), headers={'User-Agent': 'ArbiterForge-Meridian-Receiving/1.0'})
    with urlopen(request, timeout=30) as response:
        if response.status != 200 or response.geturl() != origin:
            raise ValueError('/Meridian does not resolve to the actual /Meridian/ app')
    for alias in ('meridian', 'MERIDIAN', 'mErIdIaN'):
        path = SITE + '/' + alias
        if fetch(path + '/' + query, 4_000) != ALIAS_HTML:
            raise ValueError(f'Meridian alias differs from the generated entry page: /{alias}/')
        request = Request(path + query, headers={'User-Agent': 'ArbiterForge-Meridian-Receiving/1.0'})
        with urlopen(request, timeout=30) as response:
            if response.status != 200 or response.geturl() != path + '/' + query:
                raise ValueError(f'Meridian alias does not resolve to /{alias}/ with its query')
            if response.read(len(ALIAS_HTML) + 1) != ALIAS_HTML:
                raise ValueError(f'Meridian alias differs from the generated entry page: /{alias}')
    print(f'LIVE VERIFIED: {origin} source={source_commit} verified_files={len(assets) - 1}')


def await_publication(site, source, sha):
    deadline = time.monotonic() + RECEIVE_WINDOW_SECONDS
    for attempt in count(1):
        try:
            verify(site, source, sha)
            return
        except (HTTPError, URLError, ValueError, KeyError, OSError) as error:
            remaining = deadline - time.monotonic()
            print(f'Public receiving attempt {attempt}: {error}', flush=True)
            if remaining <= 0:
                raise
            time.sleep(min(RETRY_INTERVAL_SECONDS, remaining))


if __name__ == '__main__':
    site, source, sha = sys.argv[1:4]
    if not re.fullmatch('[a-f0-9]{40}', site) or not re.fullmatch('[a-f0-9]{40}', source) or not re.fullmatch('[a-f0-9]{64}', sha):
        raise SystemExit('Expected exact site/source commits and manifest SHA-256')
    await_publication(site, source, sha)
