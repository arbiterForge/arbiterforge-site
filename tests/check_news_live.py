"""SPDX-License-Identifier: MIT. Verify public Pages responses after deployment."""
import datetime as dt
from html.parser import HTMLParser
import json
from pathlib import Path
import sys
import time
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen
import xml.etree.ElementTree as ET

BASE = 'https://arbiterforge.com'
ROOT = Path(__file__).resolve().parents[1]

class Cards(HTMLParser):
    def __init__(self):
        super().__init__(); self.keys=[]; self.tabs=0
    def handle_starttag(self, tag, attrs):
        a=dict(attrs)
        if tag=='article': self.keys.append(a.get('data-event-key'))
        if 'data-tab' in a: self.tabs+=1

def fetch(path, revision):
    # All requests are read-only and target the public site, never account APIs.
    url=BASE+path+'?deploy='+revision
    req=Request(url, headers={'User-Agent':'ArbiterNews-PublicationCheck/1.0','Cache-Control':'no-cache'})
    with urlopen(req, timeout=20) as response:
        if response.status!=200: raise ValueError(f'{path}: HTTP {response.status}')
        text=response.read(5_000_000).decode('utf-8')
    print(f'HTTP 200 {BASE}{path}', flush=True)
    return text

def verify(revision):
    files=sorted((ROOT/'_data/arbiter_news/editions').glob('*.json'))
    if not files: raise ValueError('No edition to verify')
    edition=json.loads(files[-1].read_text())
    date=edition['edition_date'];dt.date.fromisoformat(date)
    expected={s['event_key'] for s in edition['stories']}
    for path in ('/news/','/news/'+date+'/'):
        text=fetch(path,revision);page=Cards();page.feed(text)
        assert date in text and page.tabs==4, f'{path}: wrong date or tabs'
        assert len(page.keys)==len(expected) and set(page.keys)==expected, f'{path}: stale/missing stories'
        assert '{%' not in text and '{{' not in text, f'{path}: unrendered template'
    archive=fetch('/news/archive/',revision)
    assert '/news/'+date+'/' in archive, 'archive missing latest'
    coverage=json.loads(fetch('/news/coverage.json',revision))
    records=next(e['records'] for e in coverage['editions'] if e['edition_date']==date)
    assert {r['normalized_event_key'] for r in records}==expected,'coverage missing latest'
    assert len(coverage['prior_records'])==coverage['legacy_import']['record_count']
    rss=ET.fromstring(fetch('/news/feed.xml',revision))
    assert rss.findtext('./channel/item/link')==BASE+'/news/'+date+'/', 'RSS is stale'
    for asset in ['news.css','news.js']:
        assert len(fetch('/news/assets/'+asset,revision))>100
    print(f'LIVE VERIFIED: {date}, {len(expected)} stories, four tabs, archive, RSS, {len(coverage["prior_records"])} legacy records.',flush=True)

if __name__=='__main__':
    revision=sys.argv[1] if len(sys.argv)>1 else 'manual'
    if not revision.isalnum(): raise SystemExit('Revision must be alphanumeric')
    for attempt in range(1,7):
        try:
            verify(revision)
            break
        except (HTTPError, URLError, OSError, ValueError, AssertionError, StopIteration, ET.ParseError) as error:
            print(f'Public verification attempt {attempt}/6: {error}', flush=True)
            if attempt==6: raise
            time.sleep(10)
