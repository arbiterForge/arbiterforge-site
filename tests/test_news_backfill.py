"""Archive backfill contracts: never manufacture full briefings from a ledger."""
from collections import Counter
from pathlib import Path
from urllib.parse import urlsplit
import hashlib
import json
import unittest

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / '_data' / 'arbiter_news'

def load(path):
    return json.loads(path.read_text(encoding='utf-8'))

def canonical(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',',':'))

def sha(value):
    return hashlib.sha256(canonical(value).encode()).hexdigest()

class BackfillContracts(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.meta = load(DATA/'backfill.json')
        cls.pages = [load(p) for p in sorted((DATA/'archive').glob('*.json'))]
        cls.legacy = [r for p in sorted((DATA/'history_parts').glob('*.json')) for r in load(p)]

    def test_manifest_and_counts(self):
        self.assertEqual(len(self.pages),28)
        self.assertEqual(sum(p['record_count'] for p in self.pages),319)
        self.assertEqual(sum(p['restored_count'] for p in self.pages),92)
        self.assertEqual(Counter(p['archive_kind'] for p in self.pages),{'restored':7,'partial':1,'coverage-only':20})
        self.assertEqual([p['edition_date'] for p in self.pages],[r['edition_date'] for r in self.meta['dates']])
        self.assertEqual(self.meta['missing_dates'],['2026-10-06'])

    def test_every_legacy_record_preserved_exactly_once(self):
        actual = [i['record'] for p in self.pages for i in p['entries']]
        self.assertEqual(Counter(map(canonical,actual)),Counter(map(canonical,self.legacy)))
        for name,digest in self.meta['history_part_sha256'].items():
            self.assertEqual(hashlib.sha256((DATA/'history_parts'/name).read_bytes()).hexdigest(),digest)

    def test_only_recovered_text_is_called_restored(self):
        for p in self.pages:
            self.assertEqual(p['record_count'],len(p['entries']))
            self.assertEqual(p['restored_count'],sum('restored' in i for i in p['entries']))
            self.assertEqual(len({i['record']['normalized_event_key'] for i in p['entries']}),p['record_count'])
            for item in p['entries']:
                with self.subTest(date=p['edition_date'],key=item['record']['normalized_event_key']):
                    self.assertEqual(item['record_sha256'],sha(item['record']))
                    self.assertIn(item['category'],{'ai','cloud','security','money'})
                    self.assertEqual(item['record']['edition_date'],p['edition_date'])
                    if 'restored' not in item:
                        self.assertNotIn('paragraphs',item)
                        self.assertNotIn('title',item)
                        continue
                    r = item['restored']
                    self.assertTrue(r['paragraphs'])
                    self.assertTrue(all(isinstance(t,str) and t.strip() for t in r['paragraphs']))
                    self.assertRegex(r['source_sha256'],r'^[0-9a-f]{64}$')
                    self.assertEqual(r['text_sha256'],sha({k:r[k] for k in ('title','paragraphs','sources')}))
                    self.assertEqual(r['source_name'],'Arbiter-News-'+p['edition_date']+'.html')
                    for url in r['sources']:
                        u=urlsplit(url)
                        self.assertEqual(u.scheme,'https')
                        self.assertTrue(u.hostname)
                        self.assertFalse(u.username or u.password)

    def test_partial_and_missing_issues_not_fabricated(self):
        early = next(p for p in self.pages if p['edition_date']=='2026-09-29')
        self.assertEqual((early['record_count'],early['restored_count']),(24,12))
        for date in ('2026-09-26','2026-09-27'):
            p=next(p for p in self.pages if p['edition_date']==date)
            self.assertEqual((p['record_count'],p['restored_count']),(1,0))
        self.assertFalse((ROOT/'news/2026-10-06/index.html').exists())

    def test_historical_pages_exist_and_do_not_enter_daily_pipeline(self):
        daily={p.stem for p in (DATA/'editions').glob('*.json')}
        for p in self.pages:
            date=p['edition_date']
            self.assertNotIn(date,daily)
            text=(ROOT/'news'/date/'index.html').read_text(encoding='utf-8')
            self.assertIn('layout: arbiter-news-history',text)
            self.assertIn('archive_date: "'+date+'"',text)
        for filename in ('news/feed.xml','news/coverage.json'):
            text=(ROOT/filename).read_text(encoding='utf-8')
            self.assertNotIn('site.data.arbiter_news.archive',text)
        main=(ROOT/'_layouts/arbiter-news.html').read_text(encoding='utf-8')
        selection=main.split('<!doctype html>')[0]
        self.assertNotIn('site.data.arbiter_news.archive',selection)

    def test_archive_template_escapes_untrusted_historical_text(self):
        text=(ROOT/'_layouts/arbiter-news-history.html').read_text(encoding='utf-8')
        for expression in ('r.normalized_event_key | escape','r.development_summary | escape','item.restored.title | escape','paragraph | escape','url | escape'):
            self.assertIn(expression,text)
        self.assertNotIn(' hidden',text)
        self.assertIn('href="#panel-{{ cat.id }}"',text)
        self.assertIn('No missing prose has been generated.',text)
        self.assertIn('not been independently reverified',text)
        self.assertIn('Source publication date not retained',text)

if __name__=='__main__':
    unittest.main()
