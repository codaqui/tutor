from django.db import models
from utils.models import AuditModel

# Create your models here.

class Student(AuditModel):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=255)
    age = models.IntegerField()
    email = models.EmailField()
    telephone = models.CharField(max_length=20)

    def __str__(self):
        return self.name
