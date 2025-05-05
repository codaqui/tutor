from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    pass

    def get_github_data(self) -> dict:
        return self.social_auth.get(provider="github")

    def get_github_username(self) -> str:
        return self.get_github_data().extra_data.get("login")
    
    def get_github_token(self) -> str:
        return self.get_github_data().extra_data.get("access_token")
