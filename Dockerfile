FROM docker.io/nousresearch/hermes-agent:latest

USER root

RUN apt-get update && apt-get install -y python3-pip && \
    pip3 install --no-cache-dir --break-system-packages aiohttp && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

COPY server.py /app/server.py

EXPOSE 10000

ENV TERM=xterm-256color

CMD ["python3", "/app/server.py"]
