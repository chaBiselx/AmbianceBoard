from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    def test(self):
        return "toto"