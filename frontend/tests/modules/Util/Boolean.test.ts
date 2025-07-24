import { describe, it, expect } from 'vitest';
import Boolean from '../../../src/modules/Util/Boolean';

describe('Boolean.convert', () => {
    // Test avec des valeurs booléennes
    it('should return true when given the boolean true', () => {
        expect(Boolean.convert(true)).toBe(true);
    });

    it('should return false when given the boolean false', () => {
        expect(Boolean.convert(false)).toBe(false);
    });

    // Test avec des chaînes de caractères
    it('should return true for the string "true"', () => {
        expect(Boolean.convert('true')).toBe(true);
    });

    it('should return true for the string "True" (case-insensitive)', () => {
        expect(Boolean.convert('True')).toBe(true);
    });

    it('should return false for the string "false"', () => {
        expect(Boolean.convert('false')).toBe(false);
    });
    it('should return false for the int 0', () => {
        // @ts-ignore
        expect(Boolean.convert(0)).toBe(false);
    });
    it('should return false for the int 1', () => {
        // @ts-ignore
        expect(Boolean.convert(1)).toBe(false);
    });

    it('should return false for any other string', () => {
        expect(Boolean.convert('any other string')).toBe(false);
        expect(Boolean.convert('')).toBe(false);
    });

    // Test avec d'autres types (qui ne sont pas gérés explicitement mais devraient retourner false)
    it('should return false for non-string and non-boolean types', () => {
        // @ts-ignore
        expect(Boolean.convert(null)).toBe(false);
        // @ts-ignore
        expect(Boolean.convert(undefined)).toBe(false);
        // @ts-ignore
        expect(Boolean.convert(123)).toBe(false);
        // @ts-ignore
        expect(Boolean.convert(0)).toBe(false);
        // @ts-ignore
        expect(Boolean.convert({})).toBe(false);
        // @ts-ignore
        expect(Boolean.convert([])).toBe(false);
    });
});
