from fastapi import FastAPI, Request, Response, HTTPException, Path
import logging
import requests  # Import the requests library
import os
from typing import Literal, Optional
from pydantic import BaseModel, ValidationError, Field, HttpUrl
from utils.business_logic import handle_message
from utils.locales import locales

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

app = FastAPI()

# Define the base URL for the Node.js WhatsApp API service
WHATSAPP_API_URL = os.getenv(
    "WHATSAPP_API_URL", "http://whatsapp-api:3000"
)  # Use environment variable or default


@app.post("/events")
async def process_event(request: Request):
    """Receives events, processes them using business logic, and logs."""
    try:
        event_data = await request.json()

        # ignore event key.fromMe == true
        if event_data.get("key", {}).get("fromMe", False):
            logging.info("Ignoring event from self")
            return {"status": "ignored", "message": "Event ignored"}

        handle_message(event_data)
        return {
            "status": "success",
            "message": locales.get("api_event_processed", "API message missing"),
        }
    except Exception as e:
        logging.error(
            locales.get("log_error_processing_event", "Log message missing").format(
                error=e
            )
        )
        return {
            "status": "error",
            "message": locales.get("api_event_failed", "API message missing"),
        }


# Define allowed message types based on the Node.js service endpoints
AllowedMessageTypes = Literal["text", "image", "video", "audio"]


# Define Pydantic models for request body validation
class BaseMessage(BaseModel):
    jid: str = Field(
        ..., description="The recipient's JID (e.g., 1234567890@s.whatsapp.net)"
    )


class TextMessage(BaseMessage):
    message: str = Field(..., description="The text message content")


class MediaMessage(BaseMessage):
    url: HttpUrl = Field(..., description="The URL of the media file")
    caption: Optional[str] = Field(None, description="Optional caption for the media")


class AudioMessage(MediaMessage):
    ptt: bool = Field(
        False,
        description="Whether the audio should be sent as a push-to-talk voice note",
    )


@app.post("/send/{message_type}")
async def proxy_send_message(
    request: Request,
    message_type: AllowedMessageTypes = Path(..., title="The type of message to send"),
):
    """Proxies send requests (text, image, video, audio) to the Node.js WhatsApp API."""
    try:
        raw_data = await request.json()

        # Validate data based on message_type
        validated_data: BaseMessage
        if message_type == "text":
            validated_data = TextMessage(**raw_data)
        elif message_type == "audio":
            validated_data = AudioMessage(**raw_data)
        elif message_type in ["image", "video"]:
            validated_data = MediaMessage(**raw_data)
        else:
            # This case should technically not be reached due to AllowedMessageTypes
            raise HTTPException(
                status_code=400, detail=f"Invalid message type: {message_type}"
            )

        node_api_endpoint = f"{WHATSAPP_API_URL}/send/{message_type}"

        logging.info(
            f"Proxying request for message type '{message_type}' to {node_api_endpoint}"
        )

        # Forward the validated data (converted back to dict) using the requests library
        response = requests.post(
            node_api_endpoint,
            json=validated_data.dict(exclude_none=True),
            headers=dict(request.headers),
        )
        response.raise_for_status()  # Raise an exception for bad status codes (4xx or 5xx)

        # Return the response from the Node.js service
        return Response(
            content=response.content,
            status_code=response.status_code,
            media_type=response.headers.get("content-type"),
        )
    except ValidationError as e:
        logging.error(f"Validation error for /send/{message_type}: {e.errors()}")
        raise HTTPException(status_code=422, detail=e.errors())
    except requests.exceptions.RequestException as e:
        error_message = f"Error proxying /send/{message_type} to Node.js API: {e}"
        logging.error(error_message)
        # Check if the error response from Node.js has specific details
        error_detail = f"Error communicating with WhatsApp service: {e}"
        status_code = 502  # Bad Gateway
        try:
            # Try to parse the error response from the Node.js service if available
            node_error = e.response.json()
            if node_error and "error" in node_error:
                error_detail = f"WhatsApp service error: {node_error['error']}"
                # Use the status code from the Node.js response if it's a client error (4xx)
                if 400 <= e.response.status_code < 500:
                    status_code = e.response.status_code
        except Exception:
            pass  # Ignore if parsing fails or response is not JSON
        raise HTTPException(status_code=status_code, detail=error_detail)
    except Exception as e:
        logging.error(f"Error processing /send/{message_type} request: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@app.get("/")
async def root():
    return {"message": locales.get("api_service_running", "API message missing")}
