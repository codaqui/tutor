import time
import requests
from jwt import JWT, jwk_from_pem
from codaqui.settings import GH_PRIVATE_KEY_FILE, GH_APP_ID, GH_APP_INSTALL_ID



def generate_jwt_from_app():
    """
    Generates a JWT (JSON Web Token) using the GitHub App's private key.

    Returns:
        str: The encoded JWT.
    """
    with open(GH_PRIVATE_KEY_FILE, 'rb') as pem_file:
        signing_key = jwk_from_pem(pem_file.read())

    payload = {
        # Issued at time
        'iat': int(time.time()),
        # JWT expiration time (10 minutes maximum)
        'exp': int(time.time()) + 600,
        # GitHub App's ID
        'iss': GH_APP_ID
    }

    # Create JWT
    jwt_instance = JWT()
    encoded_jwt = jwt_instance.encode(payload, signing_key, alg='RS256')
    return encoded_jwt


def generate_access_token():
    """
    Generates an access token for the GitHub App installation.

    Returns:
        str: The generated access token.
    """
    jwt = generate_jwt_from_app()

    headers = {
        'Authorization': f'Bearer {jwt}',
        'Accept': 'application/vnd.github.v3+json'
    }

    url = f'https://api.github.com/app/installations/{GH_APP_INSTALL_ID}/access_tokens'
    response = requests.post(url, headers=headers)

    if response.status_code == 201:
        access_token = response.json().get('token')
        return access_token
    raise Exception('Failed to generate access token')
    
