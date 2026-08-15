FROM python:3.14-slim

WORKDIR /app
RUN useradd --create-home --uid 10001 bastion

COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

COPY agents /app/agents
COPY gateway /app/gateway
COPY identity /app/identity
COPY model_armor /app/model_armor
COPY observability /app/observability
COPY registry /app/registry
COPY runtime /app/runtime
COPY infrastructure /app/infrastructure
RUN cp /app/infrastructure/start-agent.sh /app/start-agent.sh
RUN chmod 0555 /app/start-agent.sh && chown -R bastion:bastion /app

USER bastion
ENV PYTHONPATH=/app \
    PORT=8080 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1
EXPOSE 8080
CMD ["/app/start-agent.sh"]
