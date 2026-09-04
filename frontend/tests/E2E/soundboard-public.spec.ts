import { test, expect } from '@playwright/test';

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

    const playlistId = await firstPlaylist.getAttribute('data-id');
    expect(playlistId).not.toBeNull();
    await firstPlaylist.click();

    const audio = page.locator(`.playlist-audio-${playlistId}`);
    await expect(audio).toHaveAttribute(
      'src',
      /\/public\/soundboards\/.*\/stream\?i=\d+$/,
    );
  });
});
