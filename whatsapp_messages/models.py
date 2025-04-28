from django.db import models
import requests
import os
import logging


# Create your models here.
class Message(models.Model):
    sender = models.CharField(max_length=255)
    receiver = models.CharField(max_length=255)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Message from {self.sender} to {self.receiver} at {self.timestamp}"
    
    def save(self, *args, **kwargs):
        message = send_message_via_whatsapp_api(self.receiver, self.content)
        if message:
            logging.info(f"Message sent to {self.receiver}: {self.content}")
            super().save(*args, **kwargs)
        else:
            logging.error(f"Failed to send message to {self.receiver}")
        


def send_message_via_whatsapp_api(number, message):
    """
    Sends a message via the WhatsApp API.

    Args:
        number (str): The recipient's phone number.
        message (str): The message to be sent.
    """
    jid = f"{number}@s.whatsapp.net"
    url = os.getenv("WHATSAPP_APP_URL")
    payload = {"jid": jid, "message": message}
    headers = {"Content-Type": "application/json"}

    try:
        response = requests.post(f"{url}/send/text", json=payload, headers=headers)
        logging.info(f"Response from WhatsApp API: {response.json()}")
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        return None
