from datetime import timedelta


class DurationHelper:
    @staticmethod
    def format(duration: timedelta) -> str:
        hours, remainder = divmod(int(duration.total_seconds()), 3600)
        minutes, seconds = divmod(remainder, 60)
        return f'{hours:02d}:{minutes:02d}:{seconds:02d}'