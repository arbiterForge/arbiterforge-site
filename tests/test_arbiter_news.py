"""SPDX-License-Identifier: MIT. News data contracts; no network required."""
import copy
import datetime as dt
import json
from pathlib import Path
import re
import unittest
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / '_data' / 'arbiter_news'
CATEGORIES = {'ai', 'cloud', 'security', 'money'}
DATE = re.compile(r'^\d{4}-\d{2}-\d{2}$')
FIELDS = ('event_key','topic','title','publisher','publication_date','freshness','highlights','implications','takeaway','development_summary')

def check_edition(e, known):
    """Return violations rather than mutating input or consulting live sources."""
    errors = []
    date = e.get('edition_date', '')
    if not DATE.fullmatch(date): errors.append('invalid edition date')
    else:
        try: dt.date.fromisoformat(date)
        except ValueError: errors.append('impossible edition date')
    if e.get('schema_version') != 1: errors.append('unknown schema')
    for field in ('title','intro','overview','history_note'):
        if not isinstance(e.get(field), str) or not e[field].strip(): errors.append('missing ' + field)
    stories=e.get('stories', [])
    if not isinstance(stories, list) or not stories: return errors + ['no stories']
    seen=set()
    for s in stories:
        key=s.get('event_key')
        for field in FIELDS:
            if not isinstance(s.get(field),str) or not s[field].strip(): errors.append('missing story '+field)
        if key in seen: errors.append('duplicate event in edition')
        seen.add(key)
        if s.get('category') not in CATEGORIES: errors.append('unknown category')
        if s.get('status') not in ('new','material-update'): errors.append('unknown story status')
        if key in known: errors.append('already covered event key')
        if s.get('status') == 'material-update':
            if s.get('updates_event_key') not in known or not s.get('change_summary'): errors.append('material update lacks prior event and delta')
        pub=s.get('publication_date','')
        if not DATE.fullmatch(pub): errors.append('invalid publication date')
        else:
            try:
                pubdate=dt.date.fromisoformat(pub)
                if DATE.fullmatch(date) and pubdate>dt.date.fromisoformat(date): errors.append('future publication')
            except ValueError: errors.append('impossible publication date')
        if not s.get('sources'): errors.append('missing source')
        for source in s.get('sources',[]):
            try:
                u=urlsplit(source.get('url',''))
                if u.scheme!='https' or not u.hostname or u.username or u.password: errors.append('unsafe source URL')
            except ValueError: errors.append('malformed source URL')
            if not source.get('label'): errors.append('missing source label')
    for category in CATEGORIES:
        if sum(s.get('category')==category for s in stories)<3 and not e.get('shortfalls',{}).get(category): errors.append('unexplained shortfall '+category)
    return errors

class NewsContracts(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.editions=[json.loads(p.read_text()) for p in sorted((DATA/'editions').glob('*.json'))]
        cls.legacy=[r for p in sorted((DATA/'history_parts').glob('*.json')) for r in json.loads(p.read_text())]
        cls.known={r['normalized_event_key'] for r in cls.legacy}
    def test_baseline_integrity(self):
        meta=json.loads((DATA/'history.json').read_text())
        self.assertEqual(len(self.legacy),meta['record_count'])
        for r in self.legacy:
            self.assertTrue(r['normalized_event_key'])
            self.assertIn('canonical_source_urls',r)
    def test_all_editions(self):
        known=set(self.known)
        for e in self.editions:
            with self.subTest(date=e['edition_date']):
                self.assertEqual(check_edition(e,known),[])
                path=ROOT/'news'/e['edition_date']/'index.html'
                self.assertTrue(path.exists())
                self.assertIn('layout: arbiter-news',path.read_text())
                self.assertIn('edition: "'+e['edition_date']+'"',path.read_text())
            known.update(s['event_key'] for s in e['stories'])
    def test_unsafe_sources_rejected(self):
        for url in ['javascript:alert(1)','http://example.com','https://user:password@example.com','https:///missing']:
            e=copy.deepcopy(self.editions[-1]);e['stories'][0]['sources'][0]['url']=url
            self.assertIn('unsafe source URL',check_edition(e,self.known))
    def test_duplicate_story_rejected(self):
        e=copy.deepcopy(self.editions[-1]);e['stories'].append(e['stories'][0])
        self.assertIn('duplicate event in edition',check_edition(e,self.known))
    def test_repeated_history_rejected(self):
        e=copy.deepcopy(self.editions[-1]);e['stories'][0]['event_key']=next(iter(self.known))
        self.assertIn('already covered event key',check_edition(e,self.known))
    def test_material_update_requires_evidence(self):
        e=copy.deepcopy(self.editions[-1]);e['stories'][0]['status']='material-update'
        self.assertIn('material update lacks prior event and delta',check_edition(e,self.known))
    def test_shortfall_requires_explanation(self):
        e=copy.deepcopy(self.editions[-1]);e['stories']=[s for s in e['stories'] if s['category']!='ai']
        self.assertIn('unexplained shortfall ai',check_edition(e,self.known))
        e['shortfalls']={'ai':'No additional distinct, verified developments found.'}
        self.assertNotIn('unexplained shortfall ai',check_edition(e,self.known))
    def test_templates_escape_editorial_fields(self):
        html=(ROOT/'_includes/arbiter-news-card.html').read_text()
        for name in ('title','highlights','implications','takeaway','publisher'):
            self.assertIn('s.'+name+' | escape',html)
        self.assertIn('source.url | escape',html)
    def test_no_javascript_content_is_not_hidden(self):
        html=(ROOT/'_layouts/arbiter-news.html').read_text()
        self.assertNotIn(' hidden',html)
        self.assertIn('href="#panel-{{ cat.id }}"',html)
        self.assertIn('history.replaceState',(ROOT/'news/assets/news.js').read_text())
    def test_root_domain_is_unchanged(self):
        # Only new namespaced files are added by this feature.
        cname=ROOT/'CNAME'
        if cname.exists(): self.assertEqual(cname.read_text().strip(),'arbiterforge.com')

if __name__=='__main__': unittest.main()
