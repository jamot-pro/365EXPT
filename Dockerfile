FROM docker.io/nousresearch/hermes-agent:latest

ENV HERMES_DASHBOARD=1
ENV HERMES_DASHBOARD_PORT=10000

EXPOSE 10000

CMD ["sleep", "infinity"]
