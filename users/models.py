from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    pass

    def get_github_data(self):
        return self.social_auth.get(provider='github')