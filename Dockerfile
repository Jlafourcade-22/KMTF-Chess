FROM python:3.11-slim-bookworm

# Install dependencies
RUN apt-get update && \
  apt-get install -y --no-install-recommends \
  wget \
  ca-certificates \
  && rm -rf /var/lib/apt/lists/*

# Download and install Stockfish
RUN wget https://github.com/official-stockfish/Stockfish/releases/download/sf_16.1/stockfish-ubuntu-x86-64.tar && \
  tar -xvf stockfish-ubuntu-x86-64.tar && \
  mv stockfish/stockfish-ubuntu-x86-64 /usr/bin/stockfish && \
  rm -rf stockfish-ubuntu-x86-64.tar stockfish

# Set workdir
WORKDIR /app

# Install Python deps
COPY app/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# Copy app
COPY app /app

EXPOSE 80
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80", "--reload"]
