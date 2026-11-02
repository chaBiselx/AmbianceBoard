from datetime import datetime, timedelta
from math import floor
from django.utils import timezone
from main.architecture.persistence.repository.SoundBoardRepository import SoundBoardRepository
from main.architecture.persistence.repository.UserActivityRepository import UserActivityRepository
from main.domain.common.enum.ChartPeriodEnum import ChartPeriodEnum
from main.domain.common.enum.UserActivityTypeEnum import UserActivityTypeEnum
from main.domain.common.helper.DurationHelper import DurationHelper
from main.domain.common.service.BaseActivityStatsService import BaseActivityStatsService


class ModeratorSoundboardStatsService(BaseActivityStatsService):
    def get_dashboard_listening_data(self, period='7') -> dict:
        period_choices = ChartPeriodEnum.get_days_mapping()
        selected_period = period if period in period_choices else '7'
        end_date = timezone.now()
        start_date = end_date - timedelta(days=int(selected_period))
        repository = UserActivityRepository()
        summaries = list(repository.get_soundboard_listening_summary(start_date, end_date))
        soundboards = {
            soundboard.pk: soundboard
            for soundboard in SoundBoardRepository().get_list_by_ids(
                [summary['object_id'] for summary in summaries]
            )
        }
        listeners = {}
        if summaries:
            for listener in repository.get_soundboard_listeners(start_date, end_date):
                listeners.setdefault(listener['object_id'], []).append(listener['user__username'])
        rows = []
        for summary in summaries:
            soundboard = soundboards.get(summary['object_id'])
            if soundboard is None:
                continue
            usernames = listeners.get(soundboard.pk, [])
            rows.append({
                'position': len(rows) + 1,
                'soundboard': soundboard,
                'total_duration': DurationHelper.format(summary['total_duration']),
                'average_duration': DurationHelper.format(summary['average_duration']),
                'listeners': [username for username in usernames if username is not None],
                'has_anonymous_listeners': None in usernames,
            })
        return {
            'listening_rows': rows,
            'listening_period': selected_period,
            'listening_period_choices': period_choices,
        }

    def get_soundboard_listening_time_data(self, soundboard, start_date: datetime, end_date: datetime) -> dict:
        activities = [UserActivityTypeEnum.SOUNDBOARD_VIEW]
        repository = UserActivityRepository()

        total_data = list(repository.get_total_session_duration(soundboard, start_date, end_date, activities))
        average_data = list(repository.get_average_session_duration(soundboard, start_date, end_date, activities))

        for item in total_data:
            item['activity_type'] = f"total_{item['activity_type']}"

        for item in average_data:
            item['activity_type'] = f"avg_session_{item['activity_type']}"

        nb_days = max((end_date.date() - start_date.date()).days + 1, 1)
        total_period_minutes = sum(item.get('value', 0) or 0 for item in total_data)
        average_global_daily_minutes = floor(total_period_minutes / nb_days)

        global_average_data = []
        current_date = start_date.date()
        while current_date <= end_date.date():
            global_average_data.append(
                {
                    'activity_type': 'avg_daily_global',
                    'date': current_date,
                    'value': average_global_daily_minutes,
                }
            )
            current_date += timedelta(days=1)

        merged_data = total_data + average_data + global_average_data

        return self._generated_bar_graph_data(
            start_date,
            end_date,
            merged_data,
            transposition_titles={
                f"total_{UserActivityTypeEnum.SOUNDBOARD_VIEW.value}": "Temps total d'écoute (min)",
                f"avg_session_{UserActivityTypeEnum.SOUNDBOARD_VIEW.value}": "Temps moyen/session par jour (min)",
                'avg_daily_global': "Temps moyen journalier global (min)",
            }
        )