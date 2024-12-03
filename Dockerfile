FROM python:3.10-slim

RUN apt-get update && apt-get install -y \
    build-essential \
    pkg-config \
    libavdevice-dev \
    libavfilter-dev \
    libopus-dev \
    libvpx-dev \
    libx264-dev \
    libx265-dev \
    libssl-dev \
    libffi-dev \
    python3-dev \
    && apt-get clean

WORKDIR /app
COPY . .

RUN pip install --upgrade pip setuptools wheel
RUN pip install --no-cache-dir -r requirements.txt

CMD ["python", "server.py"]
