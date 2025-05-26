# https://www.dolthub.com/blog/2025-03-19-a-pull-first-ollama-docker-image/
FROM archlinux:base

# Install Ollama using pacman (https://archlinux.org/packages/extra/x86_64/ollama/)
RUN pacman -Syu --noconfirm && \
    pacman -S --noconfirm ollama && \
    pacman -S --noconfirm curl

ENV OLLAMA_KEEP_ALIVE=24h

COPY ./entrypoint.sh /entrypoint.sh
COPY ./Modelfile /Modelfile
RUN chmod +x /entrypoint.sh

ENTRYPOINT [ "/entrypoint.sh" ]
EXPOSE 11434

CMD ["serve"]