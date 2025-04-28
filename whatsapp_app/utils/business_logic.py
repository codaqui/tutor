import logging
from utils.locales import locales
from utils.whatsapp_api import send_message_via_whatsapp_api
from utils.ollama_api import get_ollama_response
from utils.config import AUTHORIZED_USERS


def validate_sender_jid(jid: str) -> bool:
    """
    Validates if the sender's JID is authorized.
    """
    number = jid.split("@")[0]
    if number in AUTHORIZED_USERS:
        return True
    else:
        logging.warning(
            locales.get("log_unauthorized_number", "Log message missing").format(
                number=number
            )
        )
        return False


def handle_message(message_data):
    """
    Processes incoming message data and determines the appropriate response.

    Args:
        message_data (dict): The JSON data received from the WhatsApp event.

    Returns:
        str or None: The response message string, or None if no response is needed.
    """
    try:
        # Validate the incoming message data sender is authorized
        if message_data.get("type") == "notify" and "messages" in message_data:
            for message_info in message_data["messages"]:
                # Check if it's a text message (conversation)
                if (
                    "message" in message_info
                    and "conversation" in message_info["message"]
                ):
                    sender_jid = message_info.get("key", {}).get("remoteJid")

                    # Validate sender JID
                    if not validate_sender_jid(sender_jid):
                        logging.warning(
                            locales.get(
                                "log_unauthorized_number", "Log message missing"
                            ).format(number=sender_jid)
                        )
                        return None

                    text_received = message_info["message"]["conversation"]
                    logging.info(
                        locales.get("log_received_text", "Log message missing").format(
                            sender_jid=sender_jid
                        )
                    )

                    # Business logic: Get response from Ollama
                    response_text = get_ollama_response(text_received)

                    if response_text:
                        number = sender_jid.split("@")[0]
                        send_message_via_whatsapp_api(number, response_text)
                        logging.info(
                            locales.get("log_responding", "Log message missing").format(
                                sender_jid=sender_jid
                            )
                        )
                        return response_text
                    else:
                        logging.warning(
                            f"Ollama did not provide a response for prompt: {text_received}"
                        )
                        fallback_message = locales.get(
                            "error_ollama_fallback",
                            "Sorry, I couldn't process your request right now.",
                        )
                        number = sender_jid.split("@")[0]
                        send_message_via_whatsapp_api(number, fallback_message)
                        return fallback_message

                # Check if it's a Response message (extended text)
                elif (
                    "message" in message_info
                    and "extendedTextMessage" in message_info["message"]
                ):
                    sender_jid = message_info.get("key", {}).get("remoteJid")

                    # Validate sender JID
                    if not validate_sender_jid(sender_jid):
                        logging.warning(
                            locales.get(
                                "log_unauthorized_number", "Log message missing"
                            ).format(number=sender_jid)
                        )
                        return None

                    text_received = message_info["message"]["extendedTextMessage"].get(
                        "text", ""
                    )
                    logging.info(
                        locales.get("log_received_text", "Log message missing").format(
                            sender_jid=sender_jid
                        )
                    )

                    # Business logic: Get response from Ollama
                    response_text = get_ollama_response(text_received)

                    if response_text:
                        number = sender_jid.split("@")[0]
                        send_message_via_whatsapp_api(number, response_text)
                        logging.info(
                            locales.get("log_responding", "Log message missing").format(
                                sender_jid=sender_jid
                            )
                        )
                        return response_text
                    else:
                        logging.warning(
                            f"Ollama did not provide a response for prompt: {text_received}"
                        )
                        fallback_message = locales.get(
                            "error_ollama_fallback",
                            "Sorry, I couldn't process your request right now.",
                        )
                        number = sender_jid.split("@")[0]
                        send_message_via_whatsapp_api(number, fallback_message)
                        return fallback_message
                else:
                    logging.info(
                        locales.get("log_received_non_text", "Log message missing")
                    )
        else:
            event_type = message_data.get("type")
            logging.info(
                locales.get(
                    "log_received_other_event_type", "Log message missing"
                ).format(event_type=event_type)
            )

    except Exception as e:
        logging.error(
            locales.get("log_error_processing_message", "Log message missing").format(
                error=e
            )
        )
    return None
