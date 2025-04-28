import requests
from utils.config import NODEJS_WHATSAPP_API_URL
from utils.locales import locales


def send_message_via_whatsapp_api(phone_number, message):
    """
    Sends a message to a specified phone number via the WhatsApp API.

    Args:
        phone_number (str): The recipient's phone number in international format.
        message (str): The message to be sent.

    Returns:
        dict: The response from the WhatsApp API.
    """
    url = f"{NODEJS_WHATSAPP_API_URL}/send/text"
    payload = {"jid": f"{phone_number}@s.whatsapp.net", "message": message}

    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()  # Raise an error for bad responses
        return response.json()
    except requests.RequestException as e:
        print(locales["error_sending_message"].format(error=e))
        return None


def send_image_via_whatsapp_api(phone_number, url, caption=None):
    """
    Sends an image message to a specified phone number via the WhatsApp API.

    Args:
        phone_number (str): The recipient's phone number in international format.
        url (str): The URL of the image to be sent.
        caption (str, optional): The caption for the image. Defaults to None.

    Returns:
        dict: The response from the WhatsApp API or None if an error occurred.
    """
    api_url = f"{NODEJS_WHATSAPP_API_URL}/send/image"
    payload = {
        "jid": f"{phone_number}@s.whatsapp.net",
        "url": url,
        "caption": caption or "",
    }

    try:
        response = requests.post(api_url, json=payload)
        response.raise_for_status()  # Raise an error for bad responses
        return response.json()
    except requests.RequestException as e:
        print(locales["error_sending_image"].format(error=e))
        return None


def send_video_via_whatsapp_api(phone_number, url, caption=None):
    """
    Sends a video message to a specified phone number via the WhatsApp API.

    Args:
        phone_number (str): The recipient's phone number in international format.
        url (str): The URL of the video to be sent.
        caption (str, optional): The caption for the video. Defaults to None.

    Returns:
        dict: The response from the WhatsApp API or None if an error occurred.
    """
    api_url = f"{NODEJS_WHATSAPP_API_URL}/send/video"
    payload = {
        "jid": f"{phone_number}@s.whatsapp.net",
        "url": url,
        "caption": caption or "",
    }

    try:
        response = requests.post(api_url, json=payload)
        response.raise_for_status()  # Raise an error for bad responses
        return response.json()
    except requests.RequestException as e:
        print(locales["error_sending_video"].format(error=e))
        return None


def send_audio_via_whatsapp_api(phone_number, url, ptt=False):
    """
    Sends an audio message to a specified phone number via the WhatsApp API.

    Args:
        phone_number (str): The recipient's phone number in international format.
        url (str): The URL of the audio file to be sent.
        ptt (bool, optional): Whether to send as a push-to-talk (voice note).
                              Defaults to False.

    Returns:
        dict: The response from the WhatsApp API or None if an error occurred.
    """
    api_url = f"{NODEJS_WHATSAPP_API_URL}/send/audio"
    payload = {"jid": f"{phone_number}@s.whatsapp.net", "url": url, "ptt": ptt}

    try:
        response = requests.post(api_url, json=payload)
        response.raise_for_status()  # Raise an error for bad responses
        return response.json()
    except requests.RequestException as e:
        print(locales["error_sending_audio"].format(error=e))
        return None
