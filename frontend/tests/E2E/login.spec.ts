import { test, expect } from '@playwright/test';

const USERNAME = 'root';
const PASSWORD = 'root';

test.describe('Smoke', () => {
  test('login avec root et accès à l\'accueil', async ({ page }) => {
    await page.goto('/login/');
    await page.fill('#identifiant', USERNAME);
    await page.fill('#password', PASSWORD);
    await page.click('#login-button');
    await page.waitForURL('/');
    await expect(page).toHaveURL('/');
  });
});
