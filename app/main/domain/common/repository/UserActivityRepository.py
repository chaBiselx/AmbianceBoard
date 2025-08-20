from main.models.UserActivity import UserActivity

class UserActivityRepository:

    def get_activity_before(self, date):
        # Logic to retrieve user activities before the given date
        return UserActivity.objects.filter(start_date__lt=date)
    
    