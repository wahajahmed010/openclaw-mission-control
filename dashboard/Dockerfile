FROM python:3.13-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    docker-cli curl iproute2 \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir psutil

COPY server.py index.html ./

EXPOSE 8080

CMD ["python3", "server.py"]
