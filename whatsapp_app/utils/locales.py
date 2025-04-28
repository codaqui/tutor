"""
Centralized location for application text strings (locales).
"""

locales = {
    # User-facing messages
    "maintenance_message": "Estamos em manutenção",
    # Log messages
    "log_received_text": "Received text message from {sender_jid}",
    "log_responding": "Responding to {sender_jid}",
    "log_received_non_text": "Received a non-text message type",
    "log_received_other_event_type": "Received event type: {event_type}",
    "log_error_processing_message": "Error processing message: {error}",
    "log_unauthorized_number": "Unauthorized number attempted access: {number}",
    "error_unauthorized_user": "Desculpe, você não está autorizado a usar este serviço.",
    "error_ollama_fallback": "Desculpe, não consegui processar sua solicitação no momento.",
    "log_error_processing_event": "Error processing event: {error}",
    "log_proxying_request": "Proxying request for message type '{message_type}' to {node_api_endpoint}",
    "log_validation_error": "Validation error for /send/{message_type}: {errors}",
    "log_proxy_error": "Error proxying /send/{message_type} to Node.js API: {error}",
    "log_processing_send_request_error": "Error processing /send/{message_type} request: {error}",
    # API responses
    "api_service_running": "WhatsApp Event Processor Service is running",
    "api_event_processed": "Event received and processed",
    "api_event_failed": "Failed to process event",
    # Fallback/Error messages
    "error_maintenance_message_not_found": "Error: Maintenance message not found.",
    # API sending errors
    "error_sending_message": "Error sending message: {error}",
    "error_sending_image": "Error sending image: {error}",
    "error_sending_video": "Error sending video: {error}",
    "error_sending_audio": "Error sending audio: {error}",
}
