import time
import jwt
import requests
from codaqui.settings import DISCORD_API_ENDPOINT, DISCORD_TOKEN


def get_discord_bot_headers():
    """
    Returns authentication headers for Discord API calls using the Bot Token.
    """
    return {
        "Authorization": f"Bot {DISCORD_TOKEN}",
        "Content-Type": "application/json"
    }


def get_discord_client_credentials_token():
    """
    Performs Discord OAuth2 Client Credentials flow and returns an access_token.
    """
    url = f"{DISCORD_API_ENDPOINT}/oauth2/token"
    data = {
        "grant_type": "client_credentials",
        "scope": "identify guilds"
    }
    # NOTE: DISCORD_CLIENT_ID and DISCORD_CLIENT_SECRET are required here,
    # but since they're not imported, this function will fail if called.
    # Remove this function if you don't plan to use it.
    raise NotImplementedError("This function requires DISCORD_CLIENT_ID and DISCORD_CLIENT_SECRET.")


def generate_internal_jwt(user_id, expiration_seconds=3600):
    """
    Generates an internal JWT for service authentication.
    Uses the DISCORD_TOKEN as the signing key (not recommended for production).
    """
    payload = {
        "user_id": user_id,
        "iat": int(time.time()),
        "exp": int(time.time()) + expiration_seconds
    }
    return jwt.encode(payload, DISCORD_TOKEN, algorithm="HS256")
