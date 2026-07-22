FROM docker.io/nousresearch/hermes-agent:latest

USER root
RUN apt-get update && apt-get install -y wget && \
    wget -q https://github.com/tsl0922/ttyd/releases/latest/download/ttyd.x86_64 -O /usr/local/bin/ttyd && \
    chmod +x /usr/local/bin/ttyd && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

EXPOSE 10000

ENV TERM=xterm-256color
CMD ["ttyd", "-p", "10000", "-c", "hermes:hermes123", "hermes"]
