"""Verification and mounting contracts for the split Meridian Pages build."""
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import MagicMock, patch
from urllib.parse import parse_qs, urlsplit

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import check_meridian_live as receiving
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
        for alteration in ({'conclusion': 'failure'}, {'head_sha': 'c' * 40}, {'event': 'pull_request'}, {'head_repository': {'full_name': 'other/Meridian'}}):
            with self.subTest(alteration=alteration), patch.object(meridian, 'fetch', return_value=raw), patch.object(meridian, 'api', return_value={'workflow_runs': [workflow_run(**alteration)]}), self.assertRaises(ValueError):
                meridian.select_source()

    def test_finds_manual_deployment_for_the_live_sha_and_refuses_unverified_publication(self):
        raw = json.dumps(manifest()).encode()
        missing = {'workflow_runs': []}
        manual = {'workflow_runs': [workflow_run(event='workflow_dispatch')]}
        with patch.object(meridian, 'fetch', return_value=raw), patch.object(meridian, 'api', side_effect=[missing, manual]) as api:
            _, _, receipt = meridian.select_source()
        self.assertEqual(receipt['source_commit'], SOURCE)
        for call, event in zip(api.call_args_list, ('push', 'workflow_dispatch'), strict=True):
            fields = parse_qs(urlsplit(call.args[0]).query)
            self.assertEqual(fields['head_sha'], [SOURCE])
            self.assertEqual(fields['event'], [event])
        with patch.object(meridian, 'fetch', return_value=raw), patch.object(meridian, 'api', return_value=missing), self.assertRaisesRegex(ValueError, 'No successful'):
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
        with patch.object(meridian, 'fetch', return_value=b'old entry') as stale, self.assertRaisesRegex(ValueError, 'index.html'):
            meridian.receive_assets(meridian.UPSTREAM, indexed, '?checked')
        stale.assert_called_once_with(meridian.UPSTREAM + '?checked', len(HTML))
        for html in (HTML.replace(b'./assets/ui.js', b'/assets/ui.js'), HTML + b'<script>inline()</script>',
                     HTML.replace(b"connect-src 'none'", b"connect-src https:")):
            with self.assertRaises(ValueError):
                meridian.validate_html(html, indexed)

    def test_live_receiving_retries_check_fresh_bytes_for_the_same_receipt(self):
        raw = json.dumps(manifest()).encode()
        sha = meridian.digest(raw)
        receipt = json.dumps({'site_commit': SITE, 'source_commit': SOURCE, 'manifest_sha256': sha}).encode()
        observed = []

        def fetch(url, _size):
            query = parse_qs(urlsplit(url).query)
            observed.append(query)
            if urlsplit(url).path.endswith('publication.json'):
                return receipt
            if urlsplit(url).path.endswith('build.json'):
                return raw
            return ALIAS_HTML

        def visit(request, **_options):
            location, separator, query = request.full_url.partition('?')
            response = MagicMock()
            response.status = 200
            response.geturl.return_value = location + '/' + separator + query
            response.read.return_value = ALIAS_HTML
            return MagicMock(__enter__=lambda _self: response)

        with (patch.object(receiving, 'fetch', side_effect=fetch), patch.object(receiving, 'urlopen', side_effect=visit),
              patch.object(receiving, 'receive_assets', return_value=FILES) as receive,
              patch.object(receiving.time, 'time_ns', side_effect=[10, 11])):
            receiving.verify(SITE, SOURCE, sha)
            receiving.verify(SITE, SOURCE, sha)

        requests_per_check = len(observed) // 2
        self.assertEqual(observed, [
            {'publication': [SITE], 'source': [SOURCE], 'check': [str(value)]}
            for value in range(10, 12) for _ in range(requests_per_check)
        ])
        self.assertEqual([entry.args[2].split('&check=')[1] for entry in receive.call_args_list], ['10', '11'])

    def test_waits_across_the_pages_cache_age_and_stops_at_the_deadline(self):
        error = ValueError('stale manifest')
        with (patch.object(receiving, 'verify', side_effect=[error, None]) as verify,
              patch.object(receiving.time, 'monotonic', side_effect=[0, 601]),
              patch.object(receiving.time, 'sleep') as sleep):
            receiving.await_publication(SITE, SOURCE, 'c' * 64)
        self.assertEqual(verify.call_count, 2)
        sleep.assert_called_once_with(receiving.RETRY_INTERVAL_SECONDS)

        with (patch.object(receiving, 'verify', side_effect=error) as verify,
              patch.object(receiving.time, 'monotonic', side_effect=[0, receiving.RECEIVE_WINDOW_SECONDS]),
              patch.object(receiving.time, 'sleep') as sleep,
              self.assertRaisesRegex(ValueError, 'stale manifest')):
            receiving.await_publication(SITE, SOURCE, 'c' * 64)
        verify.assert_called_once()
        sleep.assert_not_called()

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
