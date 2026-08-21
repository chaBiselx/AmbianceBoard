import { test, expect } from '@playwright/test';

const USERNAME = process.env.E2E_USERNAME || 'root';
const PASSWORD = process.env.E2E_PASSWORD || 'root';

test.describe('Smoke', () => {
  test('login avec root et accès à l\'accueil', async ({ page }) => {
    await page.goto('/login/');
    await page.fill('#identifiant', USERNAME);
    await page.fill('#password', PASSWORD);
    await page.click('button[type="submit"]');
    await page.waitForURL('/');
    await expect(page).toHaveURL('/');
  });
});
