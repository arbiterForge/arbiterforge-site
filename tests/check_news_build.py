"""SPDX-License-Identifier: MIT. Check the actual GitHub Pages/Jekyll output."""
from html.parser import HTMLParser
import json
from pathlib import Path
import sys
import xml.etree.ElementTree as ET

SOURCE = Path(__file__).resolve().parents[1]
CATEGORIES = {'ai', 'cloud', 'security', 'money'}
VOID_ELEMENTS = {'area', 'base', 'br', 'col', 'embed', 'hr', 'img', 'input', 'link', 'meta', 'param', 'source', 'track', 'wbr'}


def normalized(text):
    return ' '.join(text.split())


class Page(HTMLParser):
    """Keep rendered story text separate from scripts and hidden descendants."""
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.ids = []
        self.hrefs = []
        self.articles = []
        self.tabs = []
        self.panels = []
        self.ledgers = []
        self.stylesheets = []
        self.scripts = []
        self.theme_controls = []
        self.tab_lists = 0
        self._stack = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        parent = self._stack[-1] if self._stack else {}
        ignored = parent.get('ignored', False) or tag in ('script', 'style', 'template') or 'hidden' in attrs or attrs.get('aria-hidden') == 'true'
        frame = {'tag': tag, 'attrs': attrs, 'ignored': ignored,
                 'article': parent.get('article'), 'panel': parent.get('panel')}
        if 'id' in attrs:
            self.ids.append(attrs['id'])
        if 'tabs' in attrs.get('class', '').split():
            self.tab_lists += 1
        if 'data-tab' in attrs:
            self.tabs.append({**attrs, 'inside_tab_list': any('tabs' in f['attrs'].get('class', '').split() for f in self._stack)})
        if 'data-panel' in attrs:
            frame['panel'] = attrs['data-panel']
            self.panels.append({**attrs, 'initially_hidden': ignored})
        if tag == 'article':
            article = {'key': attrs.get('data-event-key'), 'recovery': attrs.get('data-recovery'),
                       'panel': frame['panel'], 'text': [], 'hrefs': []}
            self.articles.append(article)
            frame['article'] = article
        if tag == 'a':
            self.hrefs.append(attrs.get('href', ''))
            if frame['article'] is not None and not ignored:
                frame['article']['hrefs'].append(attrs.get('href', ''))
        if any(f['tag'] == 'head' for f in self._stack):
            if tag == 'link' and 'stylesheet' in attrs.get('rel', '').split():
                self.stylesheets.append(attrs.get('href'))
            if tag == 'script' and attrs.get('src'):
                self.scripts.append(attrs['src'])
        if tag == 'button' and 'theme-toggle' in attrs.get('class', '').split():
            self.theme_controls.append(attrs)
        if tag == 'script' and attrs.get('id') == 'arbiter-coverage-ledger':
            frame['ledger'] = []
        if tag not in VOID_ELEMENTS:
            self._stack.append(frame)

    def handle_endtag(self, tag):
        for index in range(len(self._stack) - 1, -1, -1):
            if self._stack[index]['tag'] == tag:
                frame = self._stack[index]
                if 'ledger' in frame:
                    self.ledgers.append(json.loads(''.join(frame['ledger'])))
                del self._stack[index:]
                return

    def handle_data(self, text):
        if not self._stack:
            return
        frame = self._stack[-1]
        if 'ledger' in frame:
            frame['ledger'].append(text)
        if frame['article'] is not None and not frame['ignored']:
            frame['article']['text'].append(text)


def parse(text):
    page = Page()
    page.feed(text)
    return page


def check_page(page, text, output, label, *, categories=True):
    assert '{%' not in text and '{{' not in text, (label, 'unrendered Liquid')
    assert len(page.ids) == len(set(page.ids)), (label, 'duplicate HTML identifiers')
    assert all(not href.lower().startswith(('javascript:', 'data:')) for href in page.hrefs), (label, 'unsafe link')
    for asset in ('/assets/theme.css', '/news/assets/news.css'):
        assert asset in page.stylesheets, (label, 'missing head stylesheet', asset)
        assert (output / asset.lstrip('/')).is_file(), (label, 'missing stylesheet file', asset)
    for asset in ('/assets/site.js', '/news/assets/news.js'):
        assert asset in page.scripts, (label, 'missing head script', asset)
        assert (output / asset.lstrip('/')).is_file(), (label, 'missing script file', asset)
    assert len(page.theme_controls) == 1, (label, 'missing or duplicate appearance control')
    control = page.theme_controls[0]
    assert control.get('aria-label') == 'Dark appearance' and 'hidden' in control, (label, 'appearance control must be labeled and wait for JavaScript')
    if categories:
        check_categories(page, label)
    else:
        assert not page.tabs and not page.panels, (label, 'unexpected briefing tabs on archive index')


def check_categories(page, label):
    assert page.tab_lists == 1, (label, 'expected one category tab list')
    assert len(page.tabs) == len(page.panels) == 4, (label, 'missing category tab or panel')
    assert {tab['data-tab'] for tab in page.tabs} == CATEGORIES, (label, 'wrong tab categories')
    assert {panel['data-panel'] for panel in page.panels} == CATEGORIES, (label, 'wrong panel categories')
    for tab in page.tabs:
        key = tab['data-tab']
        assert tab['inside_tab_list'] and tab.get('id') == 'tab-' + key, (label, 'tab cannot be enhanced', key)
        assert tab.get('href') == '#panel-' + key, (label, 'broken category deep link', key)
    for panel in page.panels:
        key = panel['data-panel']
        assert panel.get('id') == 'panel-' + key, (label, 'panel ID does not match its tab', key)
        assert not panel['initially_hidden'], (label, 'category hidden before JavaScript', key)
        assert panel.get('aria-labelledby') in page.ids, (label, 'unlabeled category panel', key)


def article_map(page, expected, label):
    keys = [article['key'] for article in page.articles]
    assert len(keys) == len(expected) and set(keys) == set(expected), (label, 'missing, duplicate or unexpected story keys')
    return {article['key']: article for article in page.articles}


def require_text(article, value, label, field):
    assert normalized(value) in normalized(' '.join(article['text'])), (label, article['key'], 'missing visible content', field)


def require_sources(article, urls, label):
    assert set(urls).issubset(article['hrefs']), (label, article['key'], 'missing visible source links')


def check_daily(page, edition, label):
    assert len(page.ledgers) == 1, (label, 'missing or duplicate embedded coverage ledger')
    ledger = page.ledgers[0]
    date = edition['edition_date']
    source = json.loads((SOURCE / '_data/arbiter_news/editions' / (date + '.json')).read_text(encoding='utf-8'))
    assert ledger['edition_date'] == date and ledger['stories'] == source['stories'], (label, 'embedded edition differs from source data')
    expected = {record['normalized_event_key'] for record in edition['records']}
    assert {story['event_key'] for story in ledger['stories']} == expected, (label, 'coverage and embedded edition disagree')
    articles = article_map(page, expected, label)
    for story in ledger['stories']:
        article = articles[story['event_key']]
        assert article['panel'] == story['category'], (label, article['key'], 'story in wrong category')
        for field in ('title', 'topic', 'publisher', 'publication_date', 'freshness', 'highlights', 'implications', 'takeaway'):
            require_text(article, story[field], label, field)
        if story.get('event_date') and story['event_date'] != story['publication_date']:
            require_text(article, story['event_date'], label, 'event_date')
        if story.get('status') == 'material-update':
            require_text(article, story['change_summary'], label, 'change_summary')
        require_sources(article, [source['url'] for source in story['sources']], label)
        for source_link in story['sources']:
            require_text(article, source_link['label'], label, 'source label')


def check_history(page, date):
    source = json.loads((SOURCE / '_data/arbiter_news/archive' / (date + '.json')).read_text(encoding='utf-8'))
    expected = {item['record']['normalized_event_key'] for item in source['entries']}
    articles = article_map(page, expected, date)
    for item in source['entries']:
        record = item['record']
        article = articles[record['normalized_event_key']]
        assert article['panel'] == item['category'], (date, article['key'], 'historical record in wrong category')
        require_text(article, date, date, 'edition date')
        restored = item.get('restored')
        publication = (restored or {}).get('publication_date') or record.get('source_publication_date')
        if publication:
            require_text(article, publication, date, 'source publication date')
        if record.get('underlying_event_date'):
            require_text(article, record['underlying_event_date'], date, 'event date')
        if restored:
            assert article['recovery'] == 'restored', (date, article['key'], 'incorrect recovery label')
            require_text(article, restored['title'], date, 'restored title')
            for paragraph in restored['paragraphs']:
                require_text(article, paragraph, date, 'restored paragraph')
            require_sources(article, restored['sources'], date)
        else:
            assert article['recovery'] == 'coverage-only', (date, article['key'], 'incorrect coverage label')
            require_text(article, record['development_summary'], date, 'retained summary')
            require_text(article, 'No missing prose has been generated.', date, 'coverage limitation')
            require_sources(article, record['canonical_source_urls'], date)


def verify(root):
    data = json.loads((root / 'news/coverage.json').read_text())
    assert len(data['prior_records']) == data['legacy_import']['record_count']
    assert len(data['editions']) > 0
    latest = max(data['editions'], key=lambda edition: edition['edition_date'])
    for edition in data['editions']:
        path = root / 'news' / edition['edition_date'] / 'index.html'
        text = path.read_text(encoding='utf-8')
        page = parse(text)
        check_page(page, text, root, str(path))
        check_daily(page, edition, str(path))
    text = (root / 'news/index.html').read_text(encoding='utf-8')
    assert latest['edition_date'] in text, 'latest page is missing edition date'
    page = parse(text)
    check_page(page, text, root, '/news/')
    check_daily(page, latest, '/news/')
    archive = (root / 'news/archive/index.html').read_text(encoding='utf-8')
    check_page(parse(archive), archive, root, '/news/archive/', categories=False)
    assert '/news//' not in archive, 'archive has empty edition links'
    for edition in data['editions']:
        assert '/news/' + edition['edition_date'] + '/' in archive
    feed = ET.parse(root / 'news/feed.xml')
    items = feed.findall('./channel/item')
    assert len(items) == len(data['editions']), 'feed has missing or spurious items'
    assert items[0].findtext('link') == latest['url'], 'feed is not newest first'
    assert all(item.findtext('link') in {edition['url'] for edition in data['editions']} for item in items)
    print(f"Rendered Pages output OK: {len(data['editions'])} editions; {len(data['prior_records'])} legacy records; latest {latest['edition_date']}")

    # Historical archive has a separate contract: retained summaries are not daily news.
    status = json.loads((root / 'news/archive/status.json').read_text(encoding='utf-8'))
    assert status['page_count'] == 28 and status['record_count'] == 319
    assert status['restored_text_count'] == 92
    recovered_total = 0
    for item in status['dates']:
        date = item['edition_date']
        path = root / 'news' / date / 'index.html'
        text = path.read_text(encoding='utf-8')
        page = parse(text)
        check_page(page, text, root, date)
        check_history(page, date)
        assert len(page.articles) == item['records'], (date, len(page.articles), item['records'])
        assert text.count('data-recovery="restored"') == item['restored_texts'], date
        assert text.count('data-recovery="coverage-only"') == item['records'] - item['restored_texts'], date
        assert 'Historical material' in text and 'not new reporting' in text, date
        assert 'not been independently reverified' in text, date
        assert '/news/' + date + '/' in archive, date
        recovered_total += item['restored_texts']
    assert recovered_total == 92
    assert not (root / 'news/2026-10-06/index.html').exists()
    assert 'Coverage records only' in archive and 'Partial text recovery' in archive
    assert all('/news/' + date['edition_date'] + '/' in archive for date in status['dates'])
    assert len(items) == len(data['editions']), 'historical backfill flooded the daily feed'
    print('Historical output OK: 28 pages, 319 retained records, 92 restored story texts; daily latest/RSS unaffected')
    print('News presentation contracts OK: visible story content, source links, category navigation and shared appearance assets')


if __name__ == '__main__':
    verify(Path(sys.argv[1] if len(sys.argv) > 1 else '_site'))
