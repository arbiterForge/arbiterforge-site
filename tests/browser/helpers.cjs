const { expect } = require('@playwright/test');

async function stablePage(page, path, theme = 'light') {
  await page.addInitScript(selected => {
    if (!localStorage.getItem('suadtl-theme')) localStorage.setItem('suadtl-theme', selected);
    if (!localStorage.getItem('suadtl-motion')) localStorage.setItem('suadtl-motion', 'off');
  }, theme);
  const response = await page.goto(path);
  await expect(page.locator('main')).toBeVisible();
  await page.evaluate(async () => {
    await document.fonts.ready;
    const images = [...document.images].filter(image => {
      const box = image.getBoundingClientRect(); return box.top < innerHeight && box.bottom > 0;
    });
    await Promise.all(images.map(image => image.decode().catch(() => {})));
  });
  await page.mouse.move(0, 0);
  return response;
}
async function noOverflow(page) {
  const result = await page.evaluate(() => ({
    viewport: document.documentElement.clientWidth, page: document.documentElement.scrollWidth,
    offenders: [...document.querySelectorAll('main *')].filter(element => {
      const box = element.getBoundingClientRect();
      return box.width && (box.left < -1 || box.right > innerWidth + 1) && getComputedStyle(element).position !== 'absolute';
    }).slice(0, 8).map(element => element.tagName.toLowerCase() + (element.className ? '.' + String(element.className).replaceAll(' ', '.') : '')),
  }));
  expect(result.page, JSON.stringify(result)).toBeLessThanOrEqual(result.viewport + 1);
}
module.exports = { stablePage, noOverflow };
