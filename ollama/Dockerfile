# https://www.dolthub.com/blog/2025-03-19-a-pull-first-ollama-docker-image/
FROM ollama/ollama:latest AS ollama

# Alpine Linux base image
FROM alpine:latest

# Copy the Ollama binary and necessary files from the ollama stage
COPY --from=ollama /usr/bin/ollama /usr/bin/ollama

# Add packages needed for Ollama to run
RUN apk add --no-cache libstdc++ 

# Ollama configuration
ENV OLLAMA_KEEP_ALIVE=24h

# Make custom entrypoint script executable
COPY ./entrypoint.sh /entrypoint.sh
COPY ./Modelfile /Modelfile
RUN chmod +x /entrypoint.sh

ENTRYPOINT [ "/entrypoint.sh" ]
EXPOSE 11434

CMD ["serve"]