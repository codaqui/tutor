# https://www.dolthub.com/blog/2025-03-19-a-pull-first-ollama-docker-image/
FROM ollama/ollama:latest AS ollama

# Alpine Linux base image
FROM debian:stable-slim

# Set the working directory
WORKDIR /app

# Adiciona pacotes essenciais e gcompat para compatibilidade com glibc
# Adicionado strace para facilitar o debugging, caso necessário
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    ca-certificates \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copia o binário do Ollama e arquivos necessários do estágio ollama
COPY --from=ollama /bin/ollama /usr/bin/ollama
# COPY --from=ollama /lib/ollama /lib/ollama

# Copia arquivos de modelo e entrypoint
COPY ./Modelfile /app/Modelfile
COPY ./entrypoint.sh /app/entrypoint.sh

RUN chmod +x /app/entrypoint.sh /usr/bin/ollama

EXPOSE 11434

ENTRYPOINT ["/app/entrypoint.sh"]