# https://www.dolthub.com/blog/2025-03-19-a-pull-first-ollama-docker-image/
FROM ollama/ollama:latest

ENV OLLAMA_KEEP_ALIVE=24h

RUN apt-get update -y && apt-get install curl -y

COPY ./entrypoint.sh /entrypoint.sh
COPY ./Modelfile /Modelfile
RUN chmod +x /entrypoint.sh

ENTRYPOINT [ "/entrypoint.sh" ]
EXPOSE 11434

CMD ["serve"]