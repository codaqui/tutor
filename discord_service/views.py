from django.shortcuts import render
from discord_service.auth import generate_access_token


def discord_headers():
    access_token = generate_access_token()
    return {"Authorization ": f"Bot {access_token}"}


def send_message():
    url = f"https://discord.com/api/v9/channels/{channel_id}/messages"
    headers = discord_headers()
    data = {}
    response = requests.post(url, headers=headers, json=data)
    return response.json()
