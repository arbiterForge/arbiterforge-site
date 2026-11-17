"""Guard the cinematic enhancement without requiring a browser in unit CI."""
from pathlib import Path
import shutil
import subprocess
import unittest

ROOT = Path(__file__).resolve().parents[1]


class AtelierTests(unittest.TestCase):
    def test_art_is_local_and_bounded(self):
        image = (ROOT / 'assets/atelier-machine.avif').read_bytes()
        self.assertIn(b'ftypavif', image[:32])
        self.assertLess(len(image), 100_000)

    def test_hero_remains_semantic(self):
        hero = (ROOT / '_includes/cinematic-hero.html').read_text()
        self.assertIn('aria-labelledby="intro-title"', hero)
        self.assertIn('<h1 id="intro-title">', hero)
        self.assertIn('href="#projects"', hero)
        self.assertIn('href="/news/"', hero)
        self.assertIn('motion-control.html', hero)
        self.assertIn('aria-hidden="true"', hero)

    def test_shared_head_loads_enhancement_after_preferences(self):
        head = (ROOT / '_includes/theme-head.html').read_text()
        self.assertLess(head.index('/assets/motion.js'), head.index('/assets/atelier.js'))
        self.assertEqual(head.count('/assets/atelier.js'), 1)
        self.assertEqual(head.count('/assets/atelier.css'), 1)

    @unittest.skipUnless(shutil.which('node'), 'Node is needed for renderer lifecycle tests')
    def test_renderer_lifecycle(self):
        result = subprocess.run(['node', str(ROOT / 'tests/atelier-motion.cjs')],
                                cwd=ROOT, capture_output=True, text=True, timeout=20)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn('Atelier lifecycle checks passed', result.stdout)


if __name__ == '__main__':
    unittest.main()
