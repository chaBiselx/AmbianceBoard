import { test, expect, type Request } from '@playwright/test';

const SOUNDBOARD_NAME = 'E2E_Test_Soundboard_Public';

test.describe('Soundboard Public', () => {
  test('listing public accessible sans connexion', async ({ page }) => {
    const response = await page.goto('/public/soundboards');
    expect(response?.status()).toBe(200);
    await expect(page.getByText(SOUNDBOARD_NAME, { exact: false })).toBeVisible();
  });

  test('lecture des sons d\'un soundboard public sans connexion', async ({ page }) => {
    await page.goto('/public/soundboards');
    await page.getByText(SOUNDBOARD_NAME, { exact: false }).click();
    await page.waitForURL(/\/public\/soundboards\//);

    // Les boutons playlist doivent être présents
    const firstPlaylist = page.locator('.playlist-link').first();
    await expect(firstPlaylist).toBeVisible();

    // Intercepter la requête de streaming déclenchée par le clic (avant le clic)
    const streamRequest: Promise<Request> = page.waitForRequest(
      (req: Request): boolean => req.url().includes('/stream'),
      { timeout: 200 },
    );
    await firstPlaylist.click();

    const req = await streamRequest;
    expect(req.url()).toContain('/public/soundboards/');
  });
});
