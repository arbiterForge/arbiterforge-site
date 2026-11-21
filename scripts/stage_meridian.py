"""Receive Meridian's public Pages build without rebuilding or running upstream code."""
from concurrent.futures import ThreadPoolExecutor
import hashlib
import json
import os
from pathlib import Path
import re
import sys
from urllib.error import HTTPError

from stage_sim import AppDocument, SITE, api, fetch, require_run

REPOSITORY = 'SUaDtL/Meridian'
UPSTREAM = 'https://suadtl.github.io/Meridian/'
MAX_MANIFEST = 128_000
MAX_TOTAL = 30_000_000
PATH = re.compile(r'(?:index\.html|favicon\.svg|THIRD-PARTY-NOTICES\.txt|\.nojekyll|assets/[A-Za-z0-9_.-]+\.(?:js|css|svg|png|woff2))')
CSP = "default-src 'none'; script-src 'self'; style-src 'self' 'unsafe-inline'; img-src 'self' data: blob:; font-src 'self'; connect-src 'none'; worker-src 'self' blob:; object-src 'none'; base-uri 'none'; form-action 'none'"


def digest(data):
    return hashlib.sha256(data).hexdigest()


def manifest_entries(manifest, commit):
    if (manifest.get('repository') != REPOSITORY or manifest.get('commit') != commit
            or manifest.get('workingTreeDirty') is not False or manifest.get('format') != 'split-v1'
            or manifest.get('artifact') != 'index.html'):
        raise ValueError('Meridian receipt does not identify the selected clean Pages build')
    assets = manifest.get('assets')
    if not isinstance(assets, list) or not 4 <= len(assets) <= 300:
        raise ValueError('Unexpected Meridian asset count')
    indexed = {}
    for entry in assets:
        name, size, sha = entry['path'], entry['bytes'], entry['sha256']
        if (not PATH.fullmatch(name) or name in indexed or type(size) is not int
                or not 0 <= size <= MAX_TOTAL or not re.fullmatch('[a-f0-9]{64}', sha)):
            raise ValueError('Unexpected or duplicate Meridian asset')
        indexed[name] = (size, sha)
    if (not {'index.html', 'favicon.svg', 'THIRD-PARTY-NOTICES.txt', '.nojekyll'} <= indexed.keys()
            or indexed['.nojekyll'] != (0, digest(b''))
            or sum(size for size, _ in indexed.values()) != manifest.get('totalBytes')
            or manifest['totalBytes'] > MAX_TOTAL
            or indexed['index.html'] != (manifest.get('bytes'), manifest.get('sha256'))):
        raise ValueError('Incomplete or invalid Meridian asset inventory')
    initial = manifest.get('initialAssets')
    if (not isinstance(initial, list) or len(initial) != len(set(initial)) or not set(initial) <= indexed.keys()
            or 'index.html' not in initial
            or sum(indexed[name][0] for name in initial) != manifest.get('initialBytes')):
        raise ValueError('Invalid Meridian entry-point inventory')
    return indexed


class MeridianDocument(AppDocument):
    def __init__(self):
        super().__init__()
        self.resources = []
        self.modules = []
        self.disallowed = False

    def handle_starttag(self, tag, attrs):
        super().handle_starttag(tag, attrs)
        a = dict(attrs)
        if tag in ('iframe', 'base') or any(key.startswith('on') for key in a):
            self.disallowed = True
        if tag == 'script':
            if a.get('type') != 'module' or not a.get('src'):
                self.disallowed = True
            else:
                self.modules.append(a['src'])
        if tag in ('script', 'link', 'img'):
            url = a.get('src') or a.get('href')
            if url:
                self.resources.append(url)


def validate_html(data, inventory):
    text = data.decode('utf-8')
    document = MeridianDocument()
    document.feed(text)
    if (document.csp != [CSP] or document.disallowed or len(document.modules) != 1
            or '<title>Meridian' not in text):
        raise ValueError('Expected the local-only Meridian Pages application')
    for url in document.resources:
        if not url.startswith('./') or url[2:] not in inventory:
            raise ValueError('Meridian entry references an unverified or nonrelative asset')


def receive_assets(origin, indexed, query):
    size, sha = indexed['index.html']
    entry = fetch(origin + query, size)
    if len(entry) != size or digest(entry) != sha:
        raise ValueError('Meridian asset differs from the verified receipt: index.html')
    validate_html(entry, indexed)

    def receive(item):
        name, (size, sha) = item
        # GitHub Pages omits the empty .nojekyll build marker from public URLs.
        data = b'' if name == '.nojekyll' else fetch(origin + name + query, size)
        if len(data) != size or digest(data) != sha:
            raise ValueError(f'Meridian asset differs from the verified receipt: {name}')
        return name, data

    with ThreadPoolExecutor(max_workers=8) as executor:
        remaining = filter(lambda item: item[0] != 'index.html', indexed.items())
        return {'index.html': entry, **dict(executor.map(receive, remaining))}


def select_source():
    runs = api('actions/workflows/pages.yml/runs?branch=main&status=success&per_page=1',
               repository=REPOSITORY)['workflow_runs']
    if not runs:
        raise ValueError('No successful Meridian main publication')
    run = runs[0]
    require_run(run, 'pages', repository=REPOSITORY)
    if run.get('event') not in ('push', 'workflow_dispatch'):
        raise ValueError('Unexpected Meridian publication trigger')
    commit = run['head_sha']
    query = '?source=' + commit
    raw = fetch(UPSTREAM + 'build.json' + query, MAX_MANIFEST)
    manifest = json.loads(raw)
    indexed = manifest_entries(manifest, commit)
    return raw, indexed, {'format': 'arbiterforge.meridian-publication/v1', 'upstream': UPSTREAM,
                         'source_repository': REPOSITORY, 'source_commit': commit,
                         'manifest_sha256': digest(raw), 'html_sha256': manifest['sha256'],
                         'pages_run': run['html_url']}


def stage(destination, site_commit, *, poll=False, force_stage=False):
    if not re.fullmatch('[a-f0-9]{40}', site_commit):
        raise ValueError('Invalid site source commit')
    raw, indexed, receipt = select_source()
    receipt['site_commit'] = site_commit
    changed = True
    if poll:
        try:
            previous = json.loads(fetch(SITE + '/Meridian/publication.json', 20_000))
        except HTTPError as error:
            if error.code != 404:
                raise
        else:
            changed = not all(previous.get(key) == value for key, value in receipt.items() if key != 'pages_run')

    # A SIM-only change still redeploys the complete site.
    if changed or force_stage:
        assets = receive_assets(UPSTREAM, indexed, '?source=' + receipt['source_commit'])
        for name, data in {**assets, 'build.json': raw}.items():
            target = destination / name
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(data)
        (destination / 'publication.json').write_text(json.dumps(receipt, indent=2) + '\n', encoding='utf-8')
    if os.environ.get('GITHUB_OUTPUT'):
        with open(os.environ['GITHUB_OUTPUT'], 'a', encoding='utf-8') as output:
            output.write(f'changed={str(changed).lower()}\nsource_commit={receipt["source_commit"]}\n')
            output.write(f'manifest_sha256={receipt["manifest_sha256"]}\n')
    print(json.dumps({'changed': changed, **receipt}))


if __name__ == '__main__':
    stage(Path(sys.argv[1]), sys.argv[2], poll='--poll' in sys.argv[3:],
          force_stage=os.environ.get('SIM_CHANGED') == 'true')
