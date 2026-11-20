"""Verification and mounting contracts for the split Meridian Pages build."""
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import stage_meridian as meridian
from stage_meridian_aliases import ALIAS_HTML, stage_aliases

SOURCE = 'a' * 40
SITE = 'b' * 40
HTML = (f'<title>Meridian</title><meta http-equiv="Content-Security-Policy" content="{meridian.CSP}">'
        '<link rel="stylesheet" href="./assets/ui.css"><script type="module" src="./assets/ui.js"></script>').encode()
FILES = {'index.html': HTML, 'favicon.svg': b'<svg/>', 'THIRD-PARTY-NOTICES.txt': b'notice',
         '.nojekyll': b'', 'assets/ui.css': b'body{}', 'assets/ui.js': b'export{}'}


def manifest():
    return {
        'repository': meridian.REPOSITORY, 'commit': SOURCE, 'workingTreeDirty': False,
        'format': 'split-v1', 'artifact': 'index.html', 'bytes': len(HTML), 'sha256': meridian.digest(HTML),
        'initialAssets': ['index.html', 'assets/ui.js', 'assets/ui.css'],
        'initialBytes': len(HTML) + len(FILES['assets/ui.js']) + len(FILES['assets/ui.css']),
        'totalBytes': sum(map(len, FILES.values())),
        'assets': [{'path': name, 'bytes': len(data), 'sha256': meridian.digest(data)} for name, data in FILES.items()],
    }


def workflow_run(**overrides):
    return {
        'id': 1, 'head_sha': SOURCE, 'status': 'completed', 'conclusion': 'success', 'head_branch': 'main',
        'head_repository': {'full_name': meridian.REPOSITORY}, 'path': '.github/workflows/pages.yml',
        'event': 'push', 'html_url': 'https://github.com/SUaDtL/Meridian/actions/runs/1', **overrides,
    }


class MeridianPublicationTest(unittest.TestCase):
    def test_all_case_variants_alias_the_single_canonical_app(self):
        with tempfile.TemporaryDirectory() as temporary:
            destination = Path(temporary)
            canonical = destination / 'Meridian'
            canonical.mkdir()
            (canonical / 'index.html').write_bytes(HTML)
            stage_aliases(destination)
            routes = list(destination.iterdir())
            self.assertEqual(len(routes), 256)
            self.assertTrue(all(route.name.lower() == 'meridian' for route in routes))
            self.assertEqual((canonical / 'index.html').read_bytes(), HTML)
            for alias in routes:
                if alias != canonical:
                    self.assertEqual(list(alias.iterdir()), [alias / 'index.html'])
                    self.assertEqual((alias / 'index.html').read_bytes(), ALIAS_HTML)

    def test_matches_clean_manifest_to_successful_main_workflow(self):
        raw = json.dumps(manifest()).encode()
        with patch.object(meridian, 'api', return_value={'workflow_runs': [workflow_run()]}), patch.object(meridian, 'fetch', return_value=raw):
            saved, indexed, receipt = meridian.select_source()
        self.assertEqual(saved, raw)
        self.assertEqual(set(indexed), set(FILES))
        self.assertEqual(receipt['manifest_sha256'], meridian.digest(raw))
        for alteration in ({'conclusion': 'failure'}, {'event': 'pull_request'}, {'head_repository': {'full_name': 'other/Meridian'}}):
            with self.subTest(alteration=alteration), patch.object(meridian, 'api', return_value={'workflow_runs': [workflow_run(**alteration)]}), self.assertRaises(ValueError):
                meridian.select_source()

    def test_refuses_modified_or_unexpected_build_inventory(self):
        for changes in ({'commit': 'c' * 40}, {'workingTreeDirty': True}, {'totalBytes': 3}):
            with self.subTest(changes=changes), self.assertRaises(ValueError):
                meridian.manifest_entries({**manifest(), **changes}, SOURCE)
        for name in ('../CNAME', 'assets/../../index.html', 'assets/%2e%2e.js', 'assets/ui.js'):
            value = manifest()
            value['assets'].append({'path': name, 'bytes': 0, 'sha256': meridian.digest(b'')})
            with self.subTest(name=name), self.assertRaises(ValueError):
                meridian.manifest_entries(value, SOURCE)

    def test_receives_exact_public_assets_and_declines_drift(self):
        indexed = meridian.manifest_entries(manifest(), SOURCE)
        def fetch(url, _size):
            path = url.removeprefix(meridian.UPSTREAM).split('?')[0]
            return FILES[path or 'index.html']
        with patch.object(meridian, 'fetch', side_effect=fetch):
            self.assertEqual(meridian.receive_assets(meridian.UPSTREAM, indexed, '?checked'), FILES)
        with patch.object(meridian, 'fetch', side_effect=lambda url, size: b'changed' if 'ui.js' in url else fetch(url, size)), self.assertRaisesRegex(ValueError, 'assets/ui.js'):
            meridian.receive_assets(meridian.UPSTREAM, indexed, '?checked')
        for html in (HTML.replace(b'./assets/ui.js', b'/assets/ui.js'), HTML + b'<script>inline()</script>',
                     HTML.replace(b"connect-src 'none'", b"connect-src https:")):
            with self.assertRaises(ValueError):
                meridian.validate_html(html, indexed)

    def test_unchanged_poll_skips_copy_unless_sim_needs_the_combined_site(self):
        raw = json.dumps(manifest()).encode()
        indexed = meridian.manifest_entries(manifest(), SOURCE)
        receipt = {'source_commit': SOURCE, 'manifest_sha256': meridian.digest(raw)}
        previous = {**receipt, 'site_commit': SITE}
        with tempfile.TemporaryDirectory() as temporary, patch.object(meridian, 'select_source', return_value=(raw, indexed, receipt)), patch.object(meridian, 'fetch', return_value=json.dumps(previous).encode()), patch.object(meridian, 'receive_assets', return_value=FILES) as receive:
            destination = Path(temporary) / 'Meridian'
            meridian.stage(destination, SITE, poll=True)
            receive.assert_not_called()
            meridian.stage(destination, SITE, poll=True, force_stage=True)
            receive.assert_called_once()
            self.assertEqual((destination / 'build.json').read_bytes(), raw)
            self.assertEqual((destination / 'assets/ui.js').read_bytes(), FILES['assets/ui.js'])
            self.assertEqual(json.loads((destination / 'publication.json').read_bytes()), previous)
