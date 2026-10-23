"""SPDX-License-Identifier: MIT. Check the actual GitHub Pages/Jekyll output."""
from pathlib import Path
import json
import sys
import xml.etree.ElementTree as ET
from html.parser import HTMLParser

class Page(HTMLParser):
    def __init__(self):
        super().__init__();self.articles=0;self.tabs=0;self.ids=[];self.keys=[];self.hrefs=[]
    def handle_starttag(self,tag,attrs):
        a=dict(attrs)
        if 'id' in a:self.ids.append(a['id'])
        if tag=='article':self.articles+=1;self.keys.append(a.get('data-event-key'))
        if 'data-tab' in a:self.tabs+=1
        if tag=='a':self.hrefs.append(a.get('href',''))

root=Path(sys.argv[1] if len(sys.argv)>1 else '_site')
data=json.loads((root/'news/coverage.json').read_text())
assert len(data['prior_records'])==data['legacy_import']['record_count']
assert len(data['editions'])>0
latest=max(data['editions'],key=lambda e:e['edition_date'])
for edition in data['editions']:
    path=root/'news'/edition['edition_date']/'index.html'
    text=path.read_text();p=Page();p.feed(text)
    assert p.articles==len(edition['records']),(path,p.articles)
    assert p.tabs==4 and len(p.ids)==len(set(p.ids))
    assert len(p.keys)==len(set(p.keys)) and all(p.keys)
    assert '{%' not in text and '{{' not in text,'unrendered Liquid'
    assert all(not x.startswith(('javascript:','data:')) for x in p.hrefs)
    assert all('/news/assets/'+name in text for name in ('news.css','news.js'))
text=(root/'news/index.html').read_text()
assert latest['edition_date'] in text, 'latest page is missing edition date'
p=Page();p.feed(text)
assert p.articles==len(latest['records']), 'latest page has missing stories'
assert p.tabs==4 and len(p.ids)==len(set(p.ids)), 'latest navigation is invalid'
archive=(root/'news/archive/index.html').read_text()
assert '/news//' not in archive, 'archive has empty edition links'
for e in data['editions']:
    assert '/news/'+e['edition_date']+'/' in archive
for name in ['news.css','news.js']:assert (root/'news/assets'/name).exists()
feed=ET.parse(root/'news/feed.xml')
items=feed.findall('./channel/item')
assert len(items)==len(data['editions']), 'feed has missing or spurious items'
assert items[0].findtext('link')==latest['url'], 'feed is not newest first'
assert all(i.findtext('link') in {e['url'] for e in data['editions']} for i in items)
print(f"Rendered Pages output OK: {len(data['editions'])} editions; {len(data['prior_records'])} legacy records; latest {latest['edition_date']}")
