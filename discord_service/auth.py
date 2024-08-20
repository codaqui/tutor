import jwt
import requests

from codaqui.settings import DC_TOKEN, DC_VERSION

def generate_access_token():
    headers = {
        'Authorization': f'Bot {DC_TOKEN}'
    }
    response = requests.get(f'https://discord.com/api/v{DC_VERSION}', headers=headers)

    if response.status_code == 201:
        access_token = response.json().get('token')
        return access_token
    else:
        print(response.json())
        return None
    raise Exception('Failed to generate access token')
    