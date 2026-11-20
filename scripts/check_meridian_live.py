"""Verify the deployed domain path and every publicly served stage asset."""
import json
import re
import sys
import time
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from stage_meridian import MAX_MANIFEST, SITE, digest, fetch, manifest_entries, receive_assets
from stage_meridian_aliases import ALIAS_HTML


def verify(site_commit, source_commit, expected_digest):
    origin = SITE + '/Meridian/'
    query = '?publication=' + site_commit
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
        for suffix in ('', '/'):
            if fetch(SITE + '/' + alias + suffix + query, 4_000) != ALIAS_HTML:
                raise ValueError(f'Meridian alias differs from the generated entry page: /{alias}{suffix}')
    print(f'LIVE VERIFIED: {origin} source={source_commit} verified_files={len(assets) - 1}')


if __name__ == '__main__':
    site, source, sha = sys.argv[1:4]
    if not re.fullmatch('[a-f0-9]{40}', site) or not re.fullmatch('[a-f0-9]{40}', source) or not re.fullmatch('[a-f0-9]{64}', sha):
        raise SystemExit('Expected exact site/source commits and manifest SHA-256')
    for attempt in range(8):
        try:
            verify(site, source, sha)
            break
        except (HTTPError, URLError, ValueError, KeyError, OSError) as error:
            print(f'Public receiving attempt {attempt + 1}/8: {error}', flush=True)
            if attempt == 7:
                raise
            time.sleep(10)
