const { test, expect } = require('@playwright/test');
const { AxeBuilder } = require('@axe-core/playwright');
const { stablePage, noOverflow } = require('./helpers.cjs');

const routes = ['/', '/projects/', '/projects/codearbiter/', '/projects/sim/', '/projects/singedterra/', '/lab/', '/news/', '/news/archive/', '/why-hard-gates.html'];
for (const width of [320, 768, 1440]) {
  test(`site routes remain usable at ${width}px`, async ({ page }) => {
    await page.setViewportSize({ width, height: 900 });
    const errors = [];
    page.on('pageerror', error => errors.push(error.message));
    page.on('response', response => {
      if (response.status() >= 400 && !response.request().isNavigationRequest()) errors.push(`${response.status()} ${response.url()}`);
    });
    for (const path of routes) {
      const response = await stablePage(page, path);
      expect(response.status(), path).toBe(200);
      await expect(page.locator('h1'), path).toHaveCount(1);
      await noOverflow(page);
      await expect(page.locator('link[rel="canonical"]'), path).toHaveAttribute('href', 'https://arbiterforge.com' + path);
    }
    expect(errors).toEqual([]);
  });
}
for (const width of [320, 1440]) for (const theme of ['light', 'dark']) {
  test(`WCAG A/AA browser audit at ${width}px in ${theme} appearance`, async ({ page }, testInfo) => {
    test.setTimeout(120_000);
    await page.setViewportSize({ width, height: 900 });
    const reports = [];
    for (const path of routes) {
      await stablePage(page, path, theme);
      const report = await new AxeBuilder({ page }).withTags(['wcag2a', 'wcag2aa', 'wcag21aa']).analyze();
      reports.push({ path, violations: report.violations });
    }
    await testInfo.attach(`accessibility-${width}-${theme}`, { body: JSON.stringify(reports, null, 2), contentType: 'application/json' });
    const violations = reports.flatMap(report => report.violations.map(violation => ({
      path: report.path, rule: violation.id, impact: violation.impact,
      nodes: violation.nodes.map(node => ({ target: node.target, summary: node.failureSummary })),
    })));
    expect(violations).toEqual([]);
  });
}

test('skip navigation, theme persistence and hero keyboard controls', async ({ page }) => {
  await page.emulateMedia({ reducedMotion: 'no-preference' });
  await stablePage(page, '/');
  await page.keyboard.press('Tab');
  await expect(page.locator('.skip-link')).toBeFocused();
  await page.keyboard.press('Enter');
  await expect(page.locator('#main')).toBeFocused();
  await page.locator('.theme-toggle').click();
  await expect(page.locator('html')).toHaveAttribute('data-theme', 'dark');
  await page.goto('/projects/');
  await expect(page.locator('html')).toHaveAttribute('data-theme', 'dark');
  await page.goto('/');
  await expect(page.locator('[data-living-hero]')).toHaveAttribute('data-hero-ready', 'true');
  const orbit = page.locator('button[data-hero-mode="orbit"]');
  await orbit.focus();
  await page.keyboard.press('Enter');
  await expect(orbit).toHaveAttribute('aria-pressed', 'true');
  await expect(page.locator('[data-hero-pulse]')).toBeDisabled();
  await page.locator('[data-motion-toggle]').first().click();
  await expect(page.locator('html')).toHaveAttribute('data-motion', 'on');
  await expect(page.locator('[data-hero-pulse]')).toBeEnabled();
  await page.locator('[data-hero-pulse]').click();
  await page.locator('[data-motion-toggle]').first().click();
  await expect(page.locator('html')).toHaveAttribute('data-motion', 'off');
});

test('reduced motion and no-script homepage retain the reading path', async ({ browser, baseURL }) => {
  const reduced = await browser.newContext({ baseURL, reducedMotion: 'reduce' });
  const page = await reduced.newPage();
  await page.goto('/');
  await expect(page.locator('html')).toHaveAttribute('data-motion', 'off');
  await expect(page.locator('[data-hero-pulse]')).toBeDisabled();
  await page.locator('button[data-hero-mode="bloom"]').click();
  await expect(page.locator('button[data-hero-mode="bloom"]')).toHaveAttribute('aria-pressed', 'true');
  await reduced.close();
  const noScript = await browser.newContext({ baseURL, javaScriptEnabled: false, viewport: { width: 320, height: 740 } });
  const staticPage = await noScript.newPage();
  await staticPage.goto('/');
  await expect(staticPage.locator('[data-hero-fallback]')).toBeVisible();
  await expect(staticPage.locator('[data-hero-controls]')).toBeHidden();
  await expect(staticPage.getByRole('link', { name: 'View projects', exact: true })).toBeInViewport({ ratio: 1 });
  await noOverflow(staticPage);
  await noScript.close();
});

test('project examples respond to keyboard input and retain real app links', async ({ page }) => {
  await stablePage(page, '/projects/codearbiter/');
  await page.locator('[data-gate="security"]').focus();
  await page.keyboard.press('Enter');
  await expect(page.locator('[data-gate-title]')).toHaveText('Security-sensitive feature');
  await expect(page.locator('main a[href="https://codearbiter.dev/"]').first()).toBeVisible();
  await stablePage(page, '/projects/sim/');
  await page.locator('[data-sim-focus="identity"]').click();
  await expect(page.locator('[data-sim-title]')).toHaveText('Identity');
  await expect(page.locator('main a[href="/SIM/"]').first()).toBeVisible();
  await stablePage(page, '/projects/singedterra/');
  await page.locator('[data-angle]').focus();
  await page.keyboard.press('ArrowRight');
  await expect(page.locator('[data-angle-output]')).toHaveText('49°');
  await expect(page.locator('main a[href="https://suadtl.github.io/singedTerra/"]').first()).toBeVisible();
});

test('news category keyboard navigation and hash links select the same panel', async ({ page }) => {
  await stablePage(page, '/news/#panel-cloud');
  await expect(page.locator('#tab-cloud')).toHaveAttribute('aria-selected', 'true');
  await expect(page.locator('#panel-cloud')).toBeVisible();
  await page.locator('#tab-cloud').focus();
  await page.keyboard.press('ArrowRight');
  await expect(page.locator('#tab-security')).toBeFocused();
  await expect(page.locator('#panel-security')).toBeVisible();
  await expect(page).toHaveURL(/#panel-security$/);
  await page.keyboard.press('Home');
  await expect(page.locator('#tab-ai')).toBeFocused();
  await expect(page.locator('#panel-ai')).toBeVisible();
});

test('front-page headlines reach the right story and desk on click and reload', async ({ page }) => {
  await stablePage(page, '/news/2026-11-18/');
  const coverTitle = await page.locator('.lead-story h1').innerText();
  await page.getByRole('link', { name: 'Read the story' }).click();
  await expect(page.locator('article:target h3')).toHaveText(coverTitle);
  const desk = page.locator('[data-panel]:visible');
  const nextDesk = desk.locator('.desk-end a[href^="#panel-"]');
  const nextTarget = await nextDesk.getAttribute('href');
  await nextDesk.click();
  await expect(page.locator(nextTarget)).toBeFocused();
  await expect(page.locator(nextTarget + ' h2')).toBeInViewport();
  const teaser = page.locator('.desk-preview').last();
  const target = await teaser.getAttribute('href');
  await teaser.click();
  await expect(page.locator(target)).toBeFocused();
  await expect(page.locator(target)).toBeInViewport();
  await page.reload();
  await expect(page.locator(target)).toBeInViewport();
  const report = page.locator(target);
  await report.locator('summary').click();
  await expect(report.locator('.analysis-copy')).toBeVisible();
  await expect(report.locator('.sources a').first()).toBeVisible();
});

test('front-page links and disclosures work without scripts', async ({ browser, baseURL }) => {
  const context = await browser.newContext({ baseURL, javaScriptEnabled: false, viewport: { width: 320, height: 740 } });
  const page = await context.newPage();
  await page.goto('/news/2026-11-17/');
  const teaser = page.locator('.desk-preview').last();
  const target = await teaser.getAttribute('href');
  await teaser.click();
  await expect(page.locator(target)).toBeInViewport();
  await page.locator(target + ' summary').click();
  await expect(page.locator(target + ' .analysis-copy')).toBeVisible();
  await noOverflow(page);
  await context.close();
});

test('playground preserves seed links and keyboard controls', async ({ page }) => {
  await page.setViewportSize({ width: 390, height: 844 });
  await page.emulateMedia({ reducedMotion: 'no-preference' });
  await stablePage(page, '/lab/?mode=orbit&seed=2026');
  await expect(page.locator('[data-studio-mode="orbit"]')).toHaveAttribute('aria-pressed', 'true');
  await expect(page.locator('[data-studio-seed]')).toHaveValue('2026');
  await page.locator('[data-studio-mode="bloom"]').focus();
  await page.keyboard.press('Enter');
  await expect(page).toHaveURL(/mode=bloom&seed=2026/);
  await expect(page.locator('[data-studio-mode="bloom"]')).toHaveAttribute('aria-pressed', 'true');
  await page.locator('[data-motion-toggle]').first().click();
  await expect(page.locator('html')).toHaveAttribute('data-motion', 'on');
  const stage = page.locator('[data-generative="lab"]');
  const pulse = page.locator('[data-studio-impulse]');
  await pulse.scrollIntoViewIfNeeded();
  await expect(stage).not.toBeInViewport();
  await expect(pulse).toBeEnabled();
  await pulse.focus();
  await page.keyboard.press('Enter');
  await expect(stage).toBeInViewport();
  await expect(pulse).toBeFocused();
  await page.locator('[data-studio-pause]').focus();
  await page.keyboard.press('Enter');
  await expect(page.locator('[data-studio-state]')).toHaveText('Paused');
  await expect(pulse).toBeDisabled();
});

test('missing pages return a real 404 and a route home', async ({ page }) => {
  const response = await page.goto('/this-page-does-not-exist/');
  expect(response.status()).toBe(404);
  await expect(page.locator('h1')).toBeVisible();
  await expect(page.locator('meta[name="robots"]')).toHaveAttribute('content', /noindex/);
  const home = page.locator('main a[href="/"]').first();
  await expect(home).toBeVisible();
  await home.click();
  await expect(page).toHaveURL('/');
});

test('Meridian routes case variants to the canonical app and preserves URL details', async ({ page }) => {
  for (const route of ['/meridian', '/meridian/', '/MERIDIAN/', '/mErIdIaN/']) {
    const response = await page.goto(route + '?view=test#route');
    expect(response.status()).toBe(200);
    await expect(page).toHaveURL(/\/Meridian\/\?view=test#route$/);
  }
});

test('Meridian loads local assets and renders an example under /Meridian/', async ({ page, baseURL }) => {
  const failures = [];
  const requests = [];
  page.on('pageerror', error => failures.push(error.message));
  page.on('response', response => {
    if (response.status() >= 400) failures.push(response.url());
  });
  page.on('request', request => requests.push(request.url()));
  const response = await page.goto('/Meridian/');
  expect(response.status()).toBe(200);
  await page.getByRole('button', { name: 'Browse examples', exact: true }).click();
  await page.locator('.example-card').filter({ hasText: 'Edge to cloud' }).click();
  await expect(page.locator('[data-testid="rendered-diagram"] svg[data-meridian="diagram"]')).toBeVisible();
  expect(failures).toEqual([]);
  expect(requests.every(url => url.startsWith(new URL('/Meridian/', baseURL).href))).toBe(true);
});
