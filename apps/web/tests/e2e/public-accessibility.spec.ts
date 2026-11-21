import AxeBuilder from '@axe-core/playwright';
import { expect, test } from '@playwright/test';

for (const route of ['/app/login', '/app/register']) {
  test(`${route} renders without serious accessibility violations`, async ({ page }) => {
    await page.goto(route, { waitUntil: 'networkidle' });
    await expect(page.locator('main')).toBeVisible();
    const results = await new AxeBuilder({ page }).withTags(['wcag2a', 'wcag2aa', 'wcag21a', 'wcag21aa']).analyze();
    expect(results.violations.filter(item => ['serious', 'critical'].includes(item.impact || ''))).toEqual([]);
  });
}

test('protected market route stays under the /app base path', async ({ page }) => {
  await page.goto('/app/market');
  await expect(page).toHaveURL(/\/app\/(login|session\/refresh)/);
  await expect(page.getByRole('heading', { name: 'Bienvenido de nuevo' })).toBeVisible();
});
