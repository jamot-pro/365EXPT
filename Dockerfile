FROM docker.io/nousresearch/hermes-agent:latest

USER root
RUN apt-get update && apt-get install -y python3 python3-pip python3-venv && \
    python3 -m venv /opt/venv && \
    /opt/venv/bin/pip install fastapi uvicorn pydantic && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

COPY agent-services/hermes-wrapper/hermes_wrapper.py /opt/hermes_wrapper.py
COPY agent-services/hermes-wrapper/start.sh /opt/start.sh
RUN chmod +x /opt/start.sh

EXPOSE 10000
ENV PATH="/opt/venv/bin:$PATH"

CMD ["/opt/start.sh"]
