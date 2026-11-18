const { test, expect } = require('@playwright/test');
const { stablePage, noOverflow } = require('./helpers.cjs');

// Daily publishing must not rewrite a visual baseline: use a fixed dated edition.
// Missing snapshots fail normal CI. Only explicit visual:update records replacements.
const views = [
  ['home-light-1440', '/', 1440, 900, 'light'],
  ['home-dark-1440', '/', 1440, 900, 'dark'],
  ['home-light-390', '/', 390, 844, 'light'],
  ['home-light-320', '/', 320, 740, 'light'],
  ['projects-light-1440', '/projects/', 1440, 900, 'light'],
  ['codearbiter-light-390', '/projects/codearbiter/', 390, 844, 'light'],
  ['sim-dark-1440', '/projects/sim/', 1440, 900, 'dark'],
  ['playground-light-1440', '/lab/?mode=foundry&seed=2026', 1440, 900, 'light'],
  ['playground-light-390', '/lab/?mode=foundry&seed=2026', 390, 844, 'light'],
  ['news-light-1440', '/news/2026-11-17/', 1440, 900, 'light'],
  ['news-dark-390', '/news/2026-11-17/', 390, 844, 'dark'],
  ['essay-light-1440', '/why-hard-gates.html', 1440, 900, 'light'],
  ['not-found-light-390', '/this-page-does-not-exist/', 390, 844, 'light'],
];
for (const [name, path, width, height, theme] of views) {
  test(name, async ({ page }) => {
    await page.setViewportSize({ width, height });
    await stablePage(page, path, theme);
    await noOverflow(page);
    await expect(page).toHaveScreenshot(name + '.png');
  });
}

// A focused section snapshot protects all project cards without daily-edition text.
for (const width of [390, 1440]) {
  test(`home-projects-light-${width}`, async ({ page }) => {
    await page.setViewportSize({ width, height: 900 });
    await stablePage(page, '/');
    const section = page.locator('#projects');
    await section.scrollIntoViewIfNeeded();
    await section.locator('img').evaluateAll(images => Promise.all(images.map(image => image.decode())));
    await expect(section).toHaveScreenshot(`home-projects-light-${width}.png`);
  });
}
