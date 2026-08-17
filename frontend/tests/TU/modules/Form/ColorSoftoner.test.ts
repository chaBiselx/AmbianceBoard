import { describe, expect, it } from 'vitest';
import ColorSoftener from '@/modules/Form/ColorSoftoner';

describe('ColorSoftener', () => {
  it('should return a valid hex color string', () => {
    const softener = new ColorSoftener();
    const result = softener.soften('#3aa8ff');

    expect(result).toMatch(/^#[0-9a-f]{6}$/i);
  });

  it('should clamp dark colors to the minimum lightness', () => {
    const softener = new ColorSoftener();

    expect(softener.soften('#000000')).toBe('#666666');
  });

  it('should clamp bright colors to the maximum lightness', () => {
    const softener = new ColorSoftener();

    expect(softener.soften('#ffffff')).toBe('#a6a6a6');
  });

  it('should clamp saturation using default maxSaturation', () => {
    const softener = new ColorSoftener();

    expect(softener.soften('#ff0000')).toBe('#d22d2d');
  });

  it('should honor custom options and keep original full red', () => {
    const softener = new ColorSoftener({
      maxSaturation: 1,
      minLightness: 0,
      maxLightness: 1,
    });

    expect(softener.soften('#ff0000')).toBe('#ff0000');
  });
});
