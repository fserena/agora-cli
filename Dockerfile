FROM fserena/python-base:latest
LABEL author="Fernando Serena"

WORKDIR /root

RUN .env/bin/pip install --no-cache-dir agora-cli redislite "redis<3.0.0"
WORKDIR /agora

ENTRYPOINT ["/root/.env/bin/agora"]

EXPOSE 8000
