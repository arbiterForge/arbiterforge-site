"""Exercise the living hero's browser lifecycle without a browser dependency."""
from pathlib import Path
import shutil
import subprocess
import unittest

ROOT = Path(__file__).resolve().parents[1]


class LivingHeroTests(unittest.TestCase):
    @unittest.skipUnless(shutil.which('node'), 'Node is needed for renderer lifecycle tests')
    def test_renderer_lifecycle(self):
        result = subprocess.run(['node', str(ROOT / 'tests/living-hero-motion.cjs')],
                                cwd=ROOT, capture_output=True, text=True, timeout=20)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn('Living hero lifecycle checks passed', result.stdout)


if __name__ == '__main__':
    unittest.main()
