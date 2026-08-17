
class ColorSoftener {
  private maxSaturation: number;
  private minLightness: number;
  private maxLightness: number;

  constructor(options?: {
    maxSaturation?: number;
    minLightness?: number;
    maxLightness?: number;
  }) {
    this.maxSaturation = options?.maxSaturation ?? 0.65;
    this.minLightness = options?.minLightness ?? 0.4;
    this.maxLightness = options?.maxLightness ?? 0.65;
  }

  soften(hex: string): string {
    const r = parseInt(hex.slice(1, 3), 16) / 255;
    const g = parseInt(hex.slice(3, 5), 16) / 255;
    const b = parseInt(hex.slice(5, 7), 16) / 255;

    const max = Math.max(r, g, b);
    const min = Math.min(r, g, b);

    let h = 0;
    let s = 0;
    const l = (max + min) / 2;

    if (max !== min) {
      const d = max - min;

      s = l > 0.5 ? d / (2 - max - min) : d / (max + min);

      switch (max) {
        case r:
          h = (g - b) / d + (g < b ? 6 : 0);
          break;
        case g:
          h = (b - r) / d + 2;
          break;
        case b:
          h = (r - g) / d + 4;
          break;
      }

      h /= 6;
    }

    // On limite la saturation (sans trop l'écraser)
    s = Math.min(s, this.maxSaturation);

    // On garde une plage de luminosité plus large
    const adjustedL = Math.min(
      this.maxLightness,
      Math.max(this.minLightness, l)
    );

    return this.hslToHex(h * 360, s * 100, adjustedL * 100);
  }

  private hslToHex(h: number, s: number, l: number): string {
    s /= 100;
    l /= 100;

    const c = (1 - Math.abs(2 * l - 1)) * s;
    const x = c * (1 - Math.abs((h / 60) % 2 - 1));
    const m = l - c / 2;

    let r = 0;
    let g = 0;
    let b = 0;

    if (h < 60) [r, g, b] = [c, x, 0];
    else if (h < 120) [r, g, b] = [x, c, 0];
    else if (h < 180) [r, g, b] = [0, c, x];
    else if (h < 240) [r, g, b] = [0, x, c];
    else if (h < 300) [r, g, b] = [x, 0, c];
    else [r, g, b] = [c, 0, x];

    const toHex = (v: number) =>
      Math.round((v + m) * 255)
        .toString(16)
        .padStart(2, "0");

    return `#${toHex(r)}${toHex(g)}${toHex(b)}`;
  }
}
export default ColorSoftener;