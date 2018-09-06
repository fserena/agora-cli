FROM fserena/python-base:latest
LABEL author="Fernando Serena"

WORKDIR /root

RUN .env/bin/pip install agora-cli redislite
WORKDIR /agora

ENTRYPOINT ["/root/.env/bin/agora"]

EXPOSE 8000
