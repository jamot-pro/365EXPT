FROM docker.io/nousresearch/hermes-agent:latest

USER root

RUN pip3 install --no-cache-dir --break-system-packages websockets

COPY server.py /app/server.py

EXPOSE 10000

ENV TERM=xterm-256color

CMD ["python3", "/app/server.py"]
