import { describe, it, expect } from 'vitest';
import Time from '../../../src/modules/Util/Time';

describe('Time unit conversions', () => {
    it('should convert seconds to milliseconds', () => {
        expect(Time.get_seconds(2)).toBe(2000);
    });

    it('should convert minutes to milliseconds', () => {
        expect(Time.get_minutes(2)).toBe(120000);
    });

    it('should convert hours to milliseconds', () => {
        expect(Time.get_hours(2)).toBe(7200000);
    });

    it('should convert days to milliseconds', () => {
        expect(Time.get_days(2)).toBe(172800000);
    });

    it('should convert weeks to milliseconds', () => {
        expect(Time.get_weeks(2)).toBe(1209600000);
    });
});

describe('Time.formatDuration', () => {
    it('should return "0s" when the duration is zero', () => {
        expect(Time.formatDuration(0)).toBe('0s');
    });

    it('should format seconds only', () => {
        expect(Time.formatDuration(45)).toBe('45s');
    });

    it('should format minutes and seconds', () => {
        expect(Time.formatDuration(90)).toBe('1m 30s');
    });

    it('should format hours, minutes and seconds', () => {
        expect(Time.formatDuration(3661)).toBe('1h 1m 1s');
    });

    it('should format days without trailing zero units', () => {
        expect(Time.formatDuration(86400)).toBe('1d');
    });

    it('should skip minutes when they are zero but keep seconds', () => {
        expect(Time.formatDuration(3601)).toBe('1h 1s');
    });
});
