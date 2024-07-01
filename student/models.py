from django.db import models
from utils.models import AuditModel
from wallet.models import Wallet
from users.models import User
from codaqui.settings import AUTH_USER_MODEL
from datetime import datetime
from github_service.views import invite_user_to_github_team, verify_membership

# Create your models here.

class Student(AuditModel):
    id = models.BigAutoField(primary_key=True)
    user = models.OneToOneField(
        AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        default=None, 
        null=True, 
        related_name="student"
    )
    name = models.CharField(max_length=255)
    birth_year = models.IntegerField()
    email = models.EmailField()
    telephone = models.CharField(max_length=20)
    is_active = models.BooleanField(default=False)

    def __str__(self):
        return self.name
    
    def get_age(self):
        return datetime.now().year - self.birth_year
    
    def verify_github_team_membership(self):
        github_data = self.user.get_github_data()
        return verify_membership(github_data)
    
    def invite_to_github_team(self):
        github_data = self.user.get_github_data()
        invite_user_to_github_team(github_data)
    
    def active_user(self):
        wallet_exists = Wallet.objects.filter(user=self.user).exists()
        if not wallet_exists:
            Wallet.objects.create(user=self.user)
        membership = self.verify_github_team_membership()
        if membership:
            self.is_active = True
            self.save()

