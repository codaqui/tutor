#!/bin/bash

set -e  # Exit immediately if a command fails
set -o pipefail  # Exit on command pipeline failures

# Expected output from Ollama server
EXPECTED_OUTPUT="Ollama is running"
MAX_RETRIES=10  # Number of retries
SLEEP_TIME=2    # Seconds between retries

# Start Ollama server in the background
OLLAMA_HOST=127.0.0.1:11155 /bin/ollama serve &
serve_pid=$!

echo "⏳ Starting Ollama server (PID: $serve_pid)..."

# Wait for Ollama to be ready
for ((i=1; i<=MAX_RETRIES; i++)); do
    RESPONSE=$(curl -s http://localhost:11155 || echo "")

    if [[ "$RESPONSE" == "$EXPECTED_OUTPUT" ]]; then
        echo "✅ Ollama is running (Attempt $i)"
        break  # Exit loop and continue script execution
    fi

    echo "⏳ Attempt $i/$MAX_RETRIES failed. Retrying in $SLEEP_TIME seconds..."
    sleep $SLEEP_TIME
done

# If the loop completes without breaking, Ollama didn't start successfully
if [[ "$RESPONSE" != "$EXPECTED_OUTPUT" ]]; then
    echo "❌ Ollama did not start within $((MAX_RETRIES * SLEEP_TIME)) seconds"
    kill $serve_pid  # Ensure we clean up the background process
    exit 1
fi

# Continue with pulling the model
echo "🔄 Pulling model: $MODEL..."
if OLLAMA_HOST=127.0.0.1:11155 /bin/ollama create codaqui -f /Modelfile; then
    echo "✅ Successfully pulled codaqui model"
else
    echo "❌ Failed to pull model codaqui!"
    kill $serve_pid
    exit 1
fi

# Shut down the Ollama server
echo "🔄 Stopping Ollama server (PID: $serve_pid)..."
kill $serve_pid
wait $serve_pid 2>/dev/null || true  # Ensure graceful shutdown
echo "✅ Successfully shut down pulling Ollama server"

# Start Ollama in the foreground on the correct port (so container keeps running)
export OLLAMA_HOST=0.0.0.0:11434
exec /bin/ollama serve