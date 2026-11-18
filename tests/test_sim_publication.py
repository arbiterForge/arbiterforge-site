"""Publication trust, byte preservation and update contracts; fictional HTML only."""
import copy
import io
import hashlib
import importlib.util
import json
import os
import re
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from urllib.error import HTTPError
import sys

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('stage_sim', ROOT / 'scripts/stage_sim.py')
sim = importlib.util.module_from_spec(spec)
spec.loader.exec_module(sim)
live_spec = importlib.util.spec_from_file_location('check_sim_live', ROOT / 'scripts/check_sim_live.py')
with patch.dict(sys.modules, {'stage_sim': sim}):
    live = importlib.util.module_from_spec(live_spec)
    live_spec.loader.exec_module(live)
COMMIT = 'a' * 40
SITE_COMMIT = 'b' * 40
DEPLOY_GUARD = ("${{ !cancelled() && needs.build.result == 'success' && needs.build.outputs.changed == 'true' "
                "&& github.ref == 'refs/heads/main' && github.event_name != 'pull_request' "
                "&& needs.browser.result == 'success' }}")
HTML = ('''<!doctype html><title>SIM - Service Integration Map</title>
<meta http-equiv="Content-Security-Policy" content="default-src 'none'; connect-src 'none'">
<script>var build={version:`0.1.0`,commit:`''' + COMMIT + '''`,builtAt:`2026-11-17`,modified:!1};</script>
''' + ' ' * 1100).encode()


def run(workflow, event):
    return {'id': 123, 'head_sha': COMMIT, 'status': 'completed', 'conclusion': 'success',
            'head_branch': 'main', 'head_repository': {'full_name': 'SUaDtL/SIM'},
            'path': '.github/workflows/' + workflow + '.yml', 'event': event,
            'html_url': 'https://github.com/SUaDtL/SIM/actions/runs/123'}


def deployment_boundary(workflow):
    # This contract deliberately scopes assertions to the owning YAML job/step.
    # It is not a general YAML parser and fails if these owners cannot be found.
    def job(name):
        match = re.search(r'(?ms)^  ' + name + r':\n(.*?)(?=^  [a-z][a-z0-9_-]*:|\Z)', workflow)
        assert match, f'Missing {name} job'
        return match[1]
    build, browser, deploy = job('build'), job('browser'), job('deploy')
    global_permissions = re.search(r'(?m)^permissions:\n((?:  [^\n]+\n)+)', workflow)
    assert global_permissions and global_permissions[1].strip() == 'contents: read'
    assert not re.search(r'(?m)^    permissions:', build), 'Build cannot widen permissions'
    assert not re.search(r'(?m)^    permissions:', browser), 'Browser checks cannot widen permissions'
    assert "    if: needs.build.outputs.changed == 'true'\n" in browser
    assert '    needs: [build, browser]\n' in deploy, 'Deploy must depend on the checked artifact'
    assert f'    if: {DEPLOY_GUARD}\n' in deploy, 'Missing isolated deploy and quality guard'
    assert '      pages: write\n      id-token: write\n' in deploy
    assert 'contents:' not in deploy and not re.search(r'(?m)^\s+run:', deploy)
    assert 'actions/checkout@' not in deploy
    upload = re.search(r'(?ms)^      - name: Upload the Pages artifact\n(.*?)(?=^      -|\Z)', build)
    assert upload, 'Missing Pages upload owner'
    assert "        if: steps.sim.outputs.changed == 'true' && github.ref == 'refs/heads/main' && github.event_name != 'pull_request'\n" in upload[1]


class SimPublicationTest(unittest.TestCase):
    def select(self, pages=None, ci=None, html=HTML):
        responses = [{'workflow_runs': [pages or run('pages', 'workflow_run')]},
                     {'workflow_runs': [ci or run('ci', 'push')]}]
        with patch.object(sim, 'api', side_effect=responses), patch.object(sim, 'fetch', return_value=html):
            return sim.select_source()

    def test_actual_upstream_bytes_are_preserved(self):
        html, receipt = self.select()
        self.assertEqual(html, HTML)
        self.assertEqual(receipt['html_sha256'], hashlib.sha256(HTML).hexdigest())
        with tempfile.TemporaryDirectory() as temporary, patch.object(sim, 'select_source', return_value=(html, receipt)):
            sim.stage(Path(temporary), SITE_COMMIT)
            self.assertEqual((Path(temporary) / 'index.html').read_bytes(), HTML)

    def test_refuses_failed_fork_branch_or_wrong_workflow(self):
        for changes in ({'conclusion': 'failure'}, {'status': 'in_progress'},
                        {'head_branch': 'feature'}, {'head_repository': {'full_name': 'attacker/SIM'}},
                        {'path': '.github/workflows/other.yml'}):
            with self.subTest(changes=changes), self.assertRaises(ValueError):
                self.select(pages={**run('pages', 'workflow_run'), **changes})

    def test_refuses_different_ci_commit_and_pr_ci(self):
        for changes in ({'head_sha': 'c' * 40}, {'event': 'pull_request'}, {'conclusion': 'failure'}):
            with self.subTest(changes=changes), self.assertRaises(ValueError):
                self.select(ci={**run('ci', 'push'), **changes})

    def test_refuses_missing_ci(self):
        with patch.object(sim, 'api', side_effect=[{'workflow_runs': [run('pages', 'workflow_run')]}, {'workflow_runs': []}]), self.assertRaises(ValueError):
            sim.select_source()

    def test_refuses_stale_modified_external_or_online_document(self):
        for html in (HTML.replace(COMMIT.encode(), b'c' * 40), HTML.replace(b'modified:!1', b'modified:!0'),
                     HTML.replace(b"connect-src 'none'", b"connect-src https:"),
                     HTML + b'<script src="https://example.invalid/app.js"></script>',
                     HTML + b'<iframe src="https://example.invalid/"></iframe>', b'<html>Error</html>'):
            with self.subTest(html=html[:30]), self.assertRaises(ValueError):
                sim.validate_html(html, COMMIT)

    def test_failure_does_not_overwrite_existing_candidate(self):
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary)
            (path / 'index.html').write_bytes(b'old good site')
            with patch.object(sim, 'select_source', side_effect=ValueError('refused')), self.assertRaises(ValueError):
                sim.stage(path, SITE_COMMIT)
            self.assertEqual((path / 'index.html').read_bytes(), b'old good site')

    def test_schedule_skips_only_identical_site_and_app(self):
        previous = {'format': 'arbiterforge.sim-publication/v1', 'site_commit': SITE_COMMIT,
                    'source_commit': COMMIT, 'html_sha256': 'digest'}
        self.assertTrue(sim.unchanged(previous, previous))
        for key in previous:
            changed = copy.copy(previous)
            changed[key] = 'different'
            self.assertFalse(sim.unchanged(previous, changed))

    def test_poll_handles_only_initial_404_as_missing(self):
        html, receipt = self.select()
        with tempfile.TemporaryDirectory() as temporary, patch.object(sim, 'select_source', return_value=(html, receipt)):
            path = Path(temporary)
            for code in (403, 500):
                with HTTPError('url', code, 'unavailable', {}, io.BytesIO()) as error, patch.object(sim, 'fetch', side_effect=error), self.assertRaises(HTTPError):
                    sim.stage(path, SITE_COMMIT, poll=True)
                self.assertFalse((path / 'index.html').exists())
            with HTTPError('url', 404, 'missing', {}, io.BytesIO()) as error, patch.object(sim, 'fetch', side_effect=error):
                sim.stage(path, SITE_COMMIT, poll=True)
            self.assertEqual((path / 'index.html').read_bytes(), HTML)

    def test_public_receiving_rejects_stale_receipt_and_changed_bytes(self):
        import json
        receipt = {'site_commit': SITE_COMMIT, 'source_commit': COMMIT,
                   'html_sha256': hashlib.sha256(HTML).hexdigest()}
        with patch.object(live, 'fetch', return_value=json.dumps({**receipt, 'site_commit': 'c' * 40}).encode()), self.assertRaises(ValueError):
            live.verify(SITE_COMMIT, COMMIT, receipt['html_sha256'])
        with patch.object(live, 'fetch', side_effect=[json.dumps(receipt).encode(), HTML + b' ']), self.assertRaises(ValueError):
            live.verify(SITE_COMMIT, COMMIT, receipt['html_sha256'])

    def test_transport_refuses_redirects_and_size_overflow(self):
        from unittest.mock import MagicMock
        response = MagicMock()
        response.__enter__.return_value = response
        response.status = 200
        response.geturl.return_value = sim.UPSTREAM
        response.read.return_value = b'x' * 11
        with patch.object(sim, 'urlopen', return_value=response), self.assertRaises(ValueError):
            sim.fetch(sim.UPSTREAM, 10)
        response.geturl.return_value = 'https://example.invalid/'
        with patch.object(sim, 'urlopen', return_value=response), self.assertRaises(ValueError):
            sim.fetch(sim.UPSTREAM)

    def test_home_links_and_single_read_only_build(self):
        home = (ROOT / 'index.html').read_text(encoding='utf-8')
        projects = json.loads((ROOT / '_data/projects.json').read_text(encoding='utf-8'))
        self.assertEqual(next(p for p in projects if p['id'] == 'sim')['href'], '/SIM/')
        self.assertIn('href="/news/"', home)
        workflow = (ROOT / '.github/workflows/pages.yml').read_text()
        self.assertIn("cron: '7,27,47 * * * *'", workflow)
        deployment_boundary(workflow)
        self.assertIn('python tests/check_news_build.py _site', workflow)
        self.assertIn('python scripts/check_sim_live.py', workflow)

    def test_each_privileged_owner_rejects_guard_or_permission_mutations(self):
        workflow = (ROOT / '.github/workflows/pages.yml').read_text()
        guard = f'    if: {DEPLOY_GUARD}\n'
        mutations = [workflow.replace(guard, ''),
                     workflow.replace(guard, "    if: needs.build.outputs.changed == 'true'\n"),
                     workflow.replace(guard, guard.replace(" && github.event_name != 'pull_request'", '')),
                     workflow.replace('    needs: [build, browser]\n', '    needs: build\n'),
                     workflow.replace("needs.browser.result == 'success'", 'true'),
                     workflow.replace("needs.browser.result == 'success'", "(needs.browser.result == 'success' || github.event_name == 'schedule')"),
                     workflow.replace('  browser:\n', '  browser:\n    permissions:\n      contents: write\n'),
                     workflow.replace('  build:\n', '  build:\n    permissions:\n      contents: write\n'),
                     workflow.replace('      pages: write\n', '      contents: write\n      pages: write\n'),
                     workflow.replace("        if: steps.sim.outputs.changed == 'true' && github.ref == 'refs/heads/main' && github.event_name != 'pull_request'\n", '')]
        for mutated in mutations:
            self.assertNotEqual(mutated, workflow)
            with self.assertRaises(AssertionError):
                deployment_boundary(mutated)

    def test_real_poll_emits_unchanged_and_changed_outputs(self):
        html, receipt = self.select()
        previous = {**receipt, 'site_commit': SITE_COMMIT}
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            def check(old, expected):
                output = root / 'outputs'
                output.write_text('')
                with patch.object(sim, 'select_source', return_value=(html, receipt.copy())), patch.object(sim, 'fetch', return_value=json.dumps(old).encode()), patch.dict(os.environ, {'GITHUB_OUTPUT': str(output)}):
                    sim.stage(root / 'SIM', SITE_COMMIT, poll=True)
                emitted = dict(line.split('=', 1) for line in output.read_text().splitlines())
                self.assertEqual(emitted['changed'], expected)
                self.assertEqual(emitted['html_sha256'], receipt['html_sha256'])
                self.assertEqual((root / 'SIM/index.html').read_bytes(), html)
                saved = json.loads((root / 'SIM/publication.json').read_text())
                self.assertEqual(saved, previous)
            check(previous, 'false')
            for key in ['site_commit', 'source_commit', 'html_sha256']:
                check({**previous, key: 'c' * len(previous[key])}, 'true')
            # Force the stage orchestration to emit true for an unchanged receipt;
            # the exact same unchanged-output oracle must reject that fault.
            with patch.object(sim, 'unchanged', return_value=False), self.assertRaises(AssertionError):
                check(previous, 'false')


if __name__ == '__main__':
    unittest.main()
