FROM python:3.11-slim

# Install stockfish and tools
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
      stockfish \
      ca-certificates && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY app/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

COPY app /app

EXPOSE 80
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80"]
