import { describe, expect, it } from 'vitest';
import FadeModel from '@/modules/FadeStartegy';

describe('FadeSelector', () => {
    const fadeTypes = [
        'linear',
        'ease',
        'ease-in',
        'ease-out',
        'ease-in-quad',
        'ease-out-quad',
        'ease-in-out-quad',
        'ease-in-cubic',
        'ease-out-cubic',
        'ease-in-exponential',
        'ease-out-exponential',
    ];

    it.each(fadeTypes)('selects "%s" and reaches both volume endpoints', (fadeType) => {
        const strategy = FadeModel.FadeSelector.selectTypeFade(fadeType);

        expect(strategy.calculateVolume(0.2, 0.8, 0)).toBeCloseTo(0.2);
        expect(strategy.calculateVolume(0.2, 0.8, 1)).toBeCloseTo(0.8);
    });

    it('falls back to linear for an unknown type', () => {
        const strategy = FadeModel.FadeSelector.selectTypeFade('unknown');

        expect(strategy).toBeInstanceOf(FadeModel.LinearFade);
        expect(strategy.calculateVolume(0, 1, 0.25)).toBe(0.25);
    });

    it('uses the expected easing values around the midpoint', () => {
        expect(FadeModel.FadeSelector.selectTypeFade('ease-in').calculateVolume(0, 1, 0.5)).toBe(0.25);
        expect(FadeModel.FadeSelector.selectTypeFade('ease-out').calculateVolume(0, 1, 0.5)).toBe(0.75);
        expect(FadeModel.FadeSelector.selectTypeFade('ease').calculateVolume(0, 1, 0.5)).toBe(0.5);
    });
});