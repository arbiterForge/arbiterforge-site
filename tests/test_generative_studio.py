"""Contracts for the opt-in, dependency-free generative playground."""
from html.parser import HTMLParser
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]


class Elements(HTMLParser):
    def __init__(self, source):
        super().__init__()
        self.tags = []
        self.feed(source)

    def handle_starttag(self, tag, attrs):
        self.tags.append((tag, dict(attrs)))

    def with_attribute(self, name):
        return [(tag, attrs) for tag, attrs in self.tags if name in attrs]


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

    def test_living_hero_keeps_semantic_navigation_and_static_fallback(self):
        hero = (ROOT / '_includes/cinematic-hero.html').read_text()
        elements = Elements(hero)
        hosts = elements.with_attribute('data-living-hero')
        self.assertEqual(len(hosts), 1)
        self.assertEqual(hosts[0][1].get('aria-labelledby'), 'intro-title')
        self.assertTrue(any(tag == 'h1' and attrs.get('id') == 'intro-title'
                            for tag, attrs in elements.tags))
        self.assertEqual(len(elements.with_attribute('data-hero-stage')), 1)
        canvases = elements.with_attribute('data-hero-canvas')
        self.assertEqual(len(canvases), 1)
        self.assertEqual(canvases[0][0], 'canvas')
        self.assertEqual(canvases[0][1].get('aria-hidden'), 'true')
        images = elements.with_attribute('data-hero-fallback')
        self.assertEqual(len(images), 1)
        self.assertEqual(images[0][0], 'img')
        self.assertEqual(images[0][1].get('src'), '/assets/living-hero-fallback.svg')
        self.assertEqual(images[0][1].get('alt'), '')
        self.assertNotIn('hidden', images[0][1])
        self.assertTrue((ROOT / images[0][1]['src'].lstrip('/')).is_file())
        controls = elements.with_attribute('data-hero-controls')
        self.assertEqual(len(controls), 1)
        self.assertIn('hidden', controls[0][1], 'Unusable controls must stay hidden without JS')
        modes = elements.with_attribute('data-hero-mode')
        self.assertEqual({attrs['data-hero-mode'] for _, attrs in modes},
                         {'weave', 'orbit', 'bloom'})
        self.assertEqual(len(modes), 3)
        for tag, attrs in modes + elements.with_attribute('data-hero-pulse'):
            self.assertEqual(tag, 'button')
            self.assertEqual(attrs.get('type'), 'button')
        self.assertEqual(len(elements.with_attribute('data-hero-pulse')), 1)
        destinations = {attrs.get('href') for tag, attrs in elements.tags if tag == 'a'}
        self.assertTrue({'#projects', '/news/', '/lab/'}.issubset(destinations))
        self.assertFalse(elements.with_attribute('data-generative'))
        self.assertFalse(elements.with_attribute('data-machine-hero'))

    def test_home_loads_the_living_hero_without_the_old_scene(self):
        home = Elements((ROOT / 'index.html').read_text())
        scripts = [attrs.get('src') for tag, attrs in home.tags if tag == 'script']
        styles = [attrs.get('href') for tag, attrs in home.tags
                  if tag == 'link' and attrs.get('rel') == 'stylesheet']
        self.assertEqual(scripts.count('/assets/living-hero.js'), 1)
        self.assertEqual(styles.count('/assets/living-hero.css'), 1)
        self.assertNotIn('/assets/generative-studio.js', scripts)
        self.assertNotIn('/assets/generative-studio.css', styles)
        preloads = [attrs.get('href') for tag, attrs in home.tags
                    if tag == 'link' and attrs.get('rel') == 'preload']
        self.assertNotIn('/assets/atelier-machine.avif', preloads)

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
