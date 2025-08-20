

export default class Time {
    private static readonly SECOND = 1000;
    private static readonly MINUTE = 60000;
    private static readonly HOUR = 3600000;
    private static readonly DAY = 86400000;
    private static readonly WEEK = 604800000;

    static get_seconds(durationInSecond: number): number {
        return durationInSecond * Time.MINUTE / Time.SECOND
    }

    static get_minutes(durationInMinute: number): number {
        return durationInMinute * Time.MINUTE
    }

    static get_hours(durationInHour: number): number {
        return durationInHour * Time.HOUR;
    }

    static get_days(durationInDay: number): number {
        return durationInDay * Time.DAY;
    }

    static get_weeks(durationInWeek: number): number {
        return durationInWeek * Time.WEEK;
    }

}