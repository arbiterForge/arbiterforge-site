const { test, expect, devices } = require('@playwright/test');

// A repeatable browser laboratory, not CrUX, field INP, or a physical-phone benchmark.
// Chromium's four-times CPU slowdown is relative to the runner, not a named handset.
const PROFILE = {
  viewport: { width: 390, height: 844 }, cpuSlowdown: 4,
  latencyMs: 150, downloadMbps: 1.6, uploadMbps: 0.75, coldCache: true, trials: 3,
};
const BUDGET = { medianLcpMs: 2500, worstLcpMs: 4000, cls: 0.1, observedInteractionMs: 200 };

test('mobile loading, layout stability and hero response stay within budgets', async ({ browser, baseURL }, testInfo) => {
  test.setTimeout(120_000);
  const samples = [];
  for (let trial = 0; trial < PROFILE.trials; trial++) {
    const context = await browser.newContext({
      ...devices['Pixel 7'], baseURL, viewport: PROFILE.viewport,
      screen: PROFILE.viewport, reducedMotion: 'no-preference', colorScheme: 'light',
    });
    const page = await context.newPage();
    const cdp = await context.newCDPSession(page);
    await cdp.send('Network.enable');
    await cdp.send('Network.setCacheDisabled', { cacheDisabled: true });
    await cdp.send('Network.emulateNetworkConditions', {
      offline: false, latency: PROFILE.latencyMs,
      downloadThroughput: PROFILE.downloadMbps * 1_000_000 / 8,
      uploadThroughput: PROFILE.uploadMbps * 1_000_000 / 8, connectionType: 'cellular4g',
    });
    await cdp.send('Emulation.setCPUThrottlingRate', { rate: PROFILE.cpuSlowdown });
    await page.addInitScript(() => {
      localStorage.setItem('suadtl-theme', 'light');
      const result = window.__siteLab = {
        lcpMs: 0, cls: 0, longestTaskMs: 0, blockingTimeMs: 0,
        observedInteractionMs: 0, observedInteractionCount: 0, observedInputCount: 0,
        eventTimingSupported: PerformanceObserver.supportedEntryTypes.includes('event'),
      };
      new PerformanceObserver(list => {
        for (const entry of list.getEntries()) result.lcpMs = entry.startTime;
      }).observe({ type: 'largest-contentful-paint', buffered: true });
      let sessionStart = 0, sessionLast = 0, sessionValue = 0;
      new PerformanceObserver(list => {
        for (const entry of list.getEntries()) {
          if (entry.hadRecentInput) continue;
          if (sessionValue && entry.startTime - sessionLast < 1000 && entry.startTime - sessionStart < 5000) sessionValue += entry.value;
          else { sessionValue = entry.value; sessionStart = entry.startTime; }
          sessionLast = entry.startTime;
          result.cls = Math.max(result.cls, sessionValue);
        }
      }).observe({ type: 'layout-shift', buffered: true });
      new PerformanceObserver(list => {
        for (const entry of list.getEntries()) {
          result.longestTaskMs = Math.max(result.longestTaskMs, entry.duration);
          result.blockingTimeMs += Math.max(0, entry.duration - 50);
        }
      }).observe({ type: 'longtask', buffered: true });
      document.addEventListener('pointerup', () => { result.observedInputCount++; }, { passive: true });
      const interactions = new Map();
      if (result.eventTimingSupported) new PerformanceObserver(list => {
        for (const entry of list.getEntries()) {
          if (!entry.interactionId) continue;
          interactions.set(entry.interactionId, Math.max(interactions.get(entry.interactionId) || 0, entry.duration));
        }
        result.observedInteractionCount = interactions.size;
        result.observedInteractionMs = Math.max(0, ...interactions.values());
      }).observe({ type: 'event', buffered: true, durationThreshold: 16 });
    });
    const response = await page.goto('/');
    expect(response.status()).toBe(200);
    await expect(page.locator('[data-living-hero]')).toHaveAttribute('data-hero-ready', 'true');
    await page.evaluate(() => document.fonts.ready);
    // Observe a short settling period and leave animation enabled throughout input.
    await page.waitForTimeout(600);
    for (const mode of ['orbit', 'bloom', 'weave']) {
      const button = page.locator(`[data-hero-mode="${mode}"]`);
      await button.tap();
      await expect(button).toHaveAttribute('aria-pressed', 'true');
      await page.waitForTimeout(250);
    }
    await page.locator('[data-hero-pulse]').tap();
    await page.waitForTimeout(300);
    const sample = await page.evaluate(() => ({
      ...window.__siteLab,
      resources: performance.getEntriesByType('resource').map(entry => ({
        path: new URL(entry.name).pathname, transferBytes: entry.transferSize, durationMs: Math.round(entry.duration),
      })),
    }));
    expect(sample.lcpMs, 'LCP observer must produce an actual measurement').toBeGreaterThan(0);
    expect(sample.eventTimingSupported, 'Chromium must support Event Timing').toBe(true);
    expect(sample.observedInputCount, 'Four real touch inputs must reach the page').toBeGreaterThanOrEqual(4);
    samples.push(sample);
    await context.close();
  }
  const summary = {
    medianLcpMs: [...samples].map(sample => sample.lcpMs).sort((a, b) => a - b)[1],
    worstLcpMs: Math.max(...samples.map(sample => sample.lcpMs)),
    cls: Math.max(...samples.map(sample => sample.cls)),
    observedInteractionMs: Math.max(...samples.map(sample => sample.observedInteractionMs)),
  };
  const report = {
    methodology: 'Three cold Chromium mobile-emulation navigations; motion enabled, touch taps on three hero modes and pulse; local composed Pages output over emulated network and CPU slowdown. Not physical-device or field Core Web Vitals.',
    eventTimingNote: 'Longest observed interaction duration for this scripted journey. Event Timing durations under 16ms are not reported. This does not estimate a real-user 75th percentile INP.',
    profile: PROFILE, budgets: BUDGET, summary, samples,
  };
  await testInfo.attach('mobile-performance', { body: JSON.stringify(report, null, 2), contentType: 'application/json' });
  for (const [metric, limit] of Object.entries(BUDGET)) {
    expect(summary[metric], `${metric}: ${JSON.stringify(summary)}`).toBeLessThanOrEqual(limit);
  }
});
