"""Compose the public SIM main preview into Pages; never run upstream code."""
import hashlib
from html.parser import HTMLParser
import json
import os
from pathlib import Path
import re
import subprocess
import sys
from urllib.error import HTTPError
from urllib.request import Request, urlopen

REPOSITORY = 'SUaDtL/SIM'
UPSTREAM = 'https://suadtl.github.io/SIM/'
SITE = 'https://arbiterforge.com'
MAX_HTML = 10_000_000


def fetch(url, limit=MAX_HTML):
    request = Request(url, headers={'User-Agent': 'ArbiterForge-SIM-Publisher/1.0',
                                   'Cache-Control': 'no-cache'})
    with urlopen(request, timeout=30) as response:
        # No authentication is sent to the public website.
        if response.status != 200 or response.geturl().split('?')[0] != url.split('?')[0]:
            raise ValueError('Unexpected public response or redirect')
        data = response.read(limit + 1)
    if len(data) > limit:
        raise ValueError('Public response exceeds size limit')
    return data


def api(path, *, repository=REPOSITORY):
    return json.loads(subprocess.check_output(
        ['gh', 'api', f'repos/{repository}/{path}'], timeout=60))


def require_run(run, workflow, *, repository=REPOSITORY):
    if (run.get('conclusion') != 'success' or run.get('status') != 'completed'
            or run.get('head_branch') != 'main'
            or run.get('head_repository', {}).get('full_name') != repository
            or run.get('path') != f'.github/workflows/{workflow}.yml'
            or not re.fullmatch('[a-f0-9]{40}', run.get('head_sha', ''))
            or type(run.get('id')) is not int):
        raise ValueError('Untrusted or unsuccessful upstream run')


class AppDocument(HTMLParser):
    def __init__(self):
        super().__init__()
        self.csp = []
        self.external = []

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == 'meta' and a.get('http-equiv', '').lower() == 'content-security-policy':
            self.csp.append(a.get('content', ''))
        if tag in ('script', 'iframe', 'link') and (a.get('src') or a.get('href')):
            self.external.append(tag)


def validate_html(data, commit):
    if not 1000 <= len(data) <= MAX_HTML:
        raise ValueError('Invalid SIM HTML size')
    text = data.decode('utf-8')
    document = AppDocument()
    document.feed(text)
    if (len(document.csp) != 1 or document.external
            or not re.search(r"(?:^|;)\s*connect-src\s+'none'\s*(?:;|$)", document.csp[0])
            or '<title>SIM - Service Integration Map</title>' not in text):
        raise ValueError('Expected standalone offline SIM document')
    # Match the compiled build identity, not an arbitrary occurrence of the SHA.
    pattern = (r'\{version:[`\"][^`\"]+[`\"],commit:[`\"]' + re.escape(commit)
               + r'[`\"],builtAt:[`\"][^`\"]+[`\"],modified:(?:!1|false)\}')
    if not re.search(pattern, text):
        raise ValueError('Published SIM does not identify the selected clean source')


def select_source():
    pages = api('actions/workflows/pages.yml/runs?branch=main&status=success&per_page=1')['workflow_runs']
    if not pages:
        raise ValueError('No successful SIM main publication')
    published = pages[0]
    require_run(published, 'pages')
    if published.get('event') not in ('workflow_run', 'workflow_dispatch'):
        raise ValueError('Unexpected SIM publication trigger')
    commit = published['head_sha']
    runs = api(f'actions/workflows/ci.yml/runs?branch=main&event=push&status=success&head_sha={commit}&per_page=1')['workflow_runs']
    if not runs:
        raise ValueError('Published source has no successful main push CI')
    ci = runs[0]
    require_run(ci, 'ci')
    if ci['head_sha'] != commit or ci.get('event') != 'push':
        raise ValueError('CI does not match published source')
    html = fetch(UPSTREAM + '?source=' + commit)
    validate_html(html, commit)
    return html, {'format': 'arbiterforge.sim-publication/v1',
                  'upstream': UPSTREAM, 'source_repository': REPOSITORY,
                  'source_commit': commit, 'html_sha256': hashlib.sha256(html).hexdigest(),
                  'pages_run': published['html_url'], 'ci_run': ci['html_url']}


def unchanged(previous, receipt):
    return all(previous.get(k) == receipt[k]
               for k in ('format', 'site_commit', 'source_commit', 'html_sha256'))


def stage(destination, site_commit, *, poll=False):
    if not re.fullmatch('[a-f0-9]{40}', site_commit):
        raise ValueError('Invalid site source commit')
    html, receipt = select_source()
    receipt['site_commit'] = site_commit
    changed = True
    if poll:
        try:
            previous = json.loads(fetch(SITE + '/SIM/publication.json', 20_000))
        except HTTPError as error:
            if error.code != 404:
                raise
        else:
            changed = not unchanged(previous, receipt)
    # Validate everything before touching the output. Keep upstream bytes intact.
    destination.mkdir(parents=True, exist_ok=True)
    (destination / 'index.html').write_bytes(html)
    (destination / 'publication.json').write_text(json.dumps(receipt, indent=2) + '\n', encoding='utf-8')
    if os.environ.get('GITHUB_OUTPUT'):
        with open(os.environ['GITHUB_OUTPUT'], 'a', encoding='utf-8') as output:
            output.write(f'changed={str(changed).lower()}\n')
            output.write(f'html_sha256={receipt["html_sha256"]}\n')
            output.write(f'source_commit={receipt["source_commit"]}\n')
    print(json.dumps({'changed': changed, **receipt}))


if __name__ == '__main__':
    stage(Path(sys.argv[1]), sys.argv[2], poll='--poll' in sys.argv[3:])
