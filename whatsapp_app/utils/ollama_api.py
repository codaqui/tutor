import requests
import logging
import json
from utils.locales import locales
from utils.config import OLLAMA_API_URL, MODEL_NAME


def get_ollama_response(prompt):
    """
    Sends a prompt to the Ollama API and returns the generated response.

    Args:
        prompt (str): The input prompt for the Ollama model.

    Returns:
        str or None: The generated response text, or None if an error occurred.
    """
    payload = {"model": MODEL_NAME, "prompt": prompt, "stream": False}
    headers = {"Content-Type": "application/json"}

    try:
        logging.info(f"Sending prompt to Ollama.")
        response = requests.post(OLLAMA_API_URL, json=payload, headers=headers)
        response.raise_for_status()  # Raise an error for bad responses (4xx or 5xx)

        response_data = response.json()
        generated_text = response_data.get("response")

        if generated_text:
            logging.info(f"Received response from Ollama.")
            return generated_text.strip()
        else:
            logging.warning("Ollama response did not contain 'response' field.")
            return locales.get(
                "error_ollama_no_response", "Ollama did not return a response."
            )

    except requests.exceptions.RequestException as e:
        logging.error(
            locales.get("log_error_ollama_request", "Log message missing").format(
                error=e
            )
        )
        return locales.get(
            "error_ollama_request_failed", "Failed to connect to Ollama."
        )
    except Exception as e:
        logging.error(
            locales.get("log_error_ollama_processing", "Log message missing").format(
                error=e
            )
        )
        return locales.get(
            "error_ollama_processing",
            "An error occurred while processing the Ollama response.",
        )
