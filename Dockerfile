FROM docker.io/nousresearch/hermes-agent:latest

USER root

RUN pip install --no-cache-dir websockets

COPY server.py /app/server.py

EXPOSE 10000

ENV TERM=xterm-256color

CMD ["python3", "/app/server.py"]
