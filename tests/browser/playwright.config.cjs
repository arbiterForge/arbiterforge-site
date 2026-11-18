const { defineConfig } = require('@playwright/test');

// Check the already composed Pages output, including /SIM/.
// SITE_BASE_URL reuses a managed sites-preview session instead of starting a server.
const baseURL = process.env.SITE_BASE_URL || 'http://127.0.0.1:4174';
module.exports = defineConfig({
  testDir: '.', testMatch: '*.spec.cjs', outputDir: 'test-results',
  fullyParallel: false, workers: 1, retries: 0, timeout: 45_000,
  forbidOnly: !!process.env.CI, updateSnapshots: 'none',
  snapshotPathTemplate: '{testDir}/snapshots/{arg}{ext}',
  expect: {
    timeout: 8_000,
    toHaveScreenshot: { animations: 'disabled', caret: 'hide', scale: 'css', maxDiffPixelRatio: 0.002, threshold: 0.15 },
  },
  reporter: [['list'], ['html', { outputFolder: 'playwright-report', open: 'never' }]],
  use: {
    baseURL, browserName: 'chromium', viewport: { width: 1440, height: 900 },
    deviceScaleFactor: 1, colorScheme: 'light', reducedMotion: 'reduce',
    locale: 'en-US', timezoneId: 'UTC', screenshot: 'only-on-failure', trace: 'retain-on-failure',
  },
  webServer: process.env.SITE_BASE_URL ? undefined : {
    command: 'node serve.cjs', url: baseURL, reuseExistingServer: !process.env.CI, timeout: 15_000,
  },
});
