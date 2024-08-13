from django.db import models
from django.db.models.signals import pre_save, pre_delete
from django.dispatch import receiver
from utils.models import AuditModel
from codaqui.settings import AUTH_USER_MODEL

import requests

# Create your models here.
class dicordService(AuditModel):
    user = models.ForeignKey(
        AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        default=None, 
        null=True, 
        related_name="discord_service"
    )

    discordDescription = models.TextField(max_length=500, blank=True, null=True)
    discordContent = models.TextField(max_length=500, blank=True, null=True)
    discordTitle = models.CharField(max_length=100, blank=True, null=True)
    #image = models.URLField(max_length=500, blank=True, null=True)
    #thumbnail = models.URLField(max_length=500, blank=True, null=True)


    def description(self):
        return self.discordDescription

    def content(self):
        return self.discordContent
    
    def title(self):
        return self.discordTitle
    
    #def image(self):
        #return self.image
    
    #def thumbnail(self):
        #return self.thumbnail