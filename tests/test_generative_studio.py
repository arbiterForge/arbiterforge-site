"""Contracts for the opt-in, dependency-free generative playground."""
from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[1]


class GenerativeStudioContracts(unittest.TestCase):
    def test_lab_has_semantic_controls_and_fallback(self):
        text = (ROOT / 'lab/index.html').read_text()
        for required in ('data-generative="lab"', 'data-generative-scene',
                         'data-studio-mode="foundry"', 'data-studio-mode="filaments"',
                         'data-studio-mode="bloom"', 'data-studio-mode="orbit"',
                         'data-studio-seed', 'data-studio-speed', 'data-studio-density',
                         'data-studio-reroll', 'data-studio-pause', 'data-studio-share',
                         'data-studio-capture', 'data-studio-status', '<noscript>',
                         'href="/"', 'aria-label="Main navigation"'):
            self.assertIn(required, text)
        self.assertIn('role="status"', text)
        self.assertIn('tabindex="0"', text)

    def test_shared_hero_points_to_lab_and_preserves_fallback_art(self):
        hero = (ROOT / '_includes/cinematic-hero.html').read_text()
        home = (ROOT / 'index.html').read_text()
        self.assertIn('data-generative="hero"', hero)
        self.assertIn('data-generative-scene', hero)
        self.assertIn('machine-image', hero)
        self.assertIn('href="/lab/"', hero)
        self.assertIn('href="/lab/"', home)
        self.assertIn('href="#projects"', home)
        self.assertIn('href="/news/"', home)

    def test_renderer_has_bounded_motion_and_no_remote_dependencies(self):
        text = (ROOT / 'assets/generative-studio.js').read_text()
        for required in ('sceneData(seed,mode)', 'Math.min(delta,100)',
                         'Math.sqrt(maxPixels/(width*height))',
                         "document.addEventListener('visibilitychange'",
                         'IntersectionObserver', 'ResizeObserver',
                         'prefersReduced.matches', "connection?.saveData",
                         "root.dataset.motion==='on'", 'cancelAnimationFrame',
                         'data-studio-seed', 'data-studio-capture',
                         "history.replaceState(null,'',u)", 'randomGen(seed'):
            self.assertIn(required, text)
        for unwanted in ('fetch(', 'XMLHttpRequest', 'WebSocket(', 'eval(', 'new Function(', 'innerHTML ='):
            self.assertNotIn(unwanted, text)
        self.assertLess(len(text.encode()), 30000)

    def test_source_is_lightweight_and_site_assets_are_local(self):
        source = (ROOT / 'lab/index.html').read_text()
        self.assertRegex(source, r'src="/assets/generative-studio\.js"')
        self.assertRegex(source, r'href="/assets/generative-studio\.css"')
        self.assertNotRegex(source, r'<script[^>]+src="https?://')
        self.assertLess((ROOT / 'assets/generative-studio.css').stat().st_size, 12000)


if __name__ == '__main__':
    unittest.main()
