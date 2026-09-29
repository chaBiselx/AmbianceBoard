import { describe, it, expect } from 'vitest';
import { DataProcessor } from '../../../src/modules/Util/DataProcessor';

describe('DataProcessor.generateDateRange', () => {
    it('should generate a list of dates between two dates', () => {
        expect(DataProcessor.generateDateRange('2026-01-01', '2026-01-03')).toEqual([
            '2026-01-01',
            '2026-01-02',
            '2026-01-03',
        ]);
    });

    it('should generate a single date when start equals end', () => {
        expect(DataProcessor.generateDateRange('2026-01-01', '2026-01-01')).toEqual(['2026-01-01']);
    });

    it('should throw an error when start date is after end date', () => {
        expect(() => DataProcessor.generateDateRange('2026-01-03', '2026-01-01')).toThrow(
            'La date de début doit être antérieure à la date de fin'
        );
    });
});

describe('DataProcessor.createDataDictionary', () => {
    it('should build a dictionary from valid items', () => {
        const dictionary = DataProcessor.createDataDictionary([
            { date: '2026-01-01', count: 5 },
            { date: '2026-01-02', count: 10 },
        ]);
        expect(dictionary).toEqual({ '2026-01-01': 5, '2026-01-02': 10 });
    });

    it('should ignore items with a missing date', () => {
        // @ts-ignore
        const dictionary = DataProcessor.createDataDictionary([{ count: 5 }]);
        expect(dictionary).toEqual({});
    });

    it('should ignore items with a non-number count', () => {
        // @ts-ignore
        const dictionary = DataProcessor.createDataDictionary([{ date: '2026-01-01', count: '5' }]);
        expect(dictionary).toEqual({});
    });
});

describe('DataProcessor.fillMissingDatas', () => {
    it('should fill missing dates with the default value 0', () => {
        const result = DataProcessor.fillMissingDatas(['2026-01-01', '2026-01-02'], { '2026-01-01': 3 });
        expect(result).toEqual([3, 0]);
    });

    it('should fill missing dates with a custom default value', () => {
        const result = DataProcessor.fillMissingDatas(['2026-01-01', '2026-01-02'], { '2026-01-01': 3 }, -1);
        expect(result).toEqual([3, -1]);
    });
});

describe('DataProcessor.validateRequiredData', () => {
    it('should not throw when all required fields are present', () => {
        expect(() => DataProcessor.validateRequiredData({ a: 1, b: 'x' }, ['a', 'b'])).not.toThrow();
    });

    it('should throw when required fields are missing', () => {
        expect(() => DataProcessor.validateRequiredData({ a: 1 }, ['a', 'b', 'c'])).toThrow(
            'Champs requis manquants: b, c'
        );
    });

    it('should treat null values as missing', () => {
        expect(() => DataProcessor.validateRequiredData({ a: null }, ['a'])).toThrow(
            'Champs requis manquants: a'
        );
    });
});
