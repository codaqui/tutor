from django.db import models
from utils.models import AuditModel
from codaqui.settings import AUTH_USER_MODEL
from datetime import datetime

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