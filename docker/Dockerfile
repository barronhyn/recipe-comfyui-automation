FROM python:3.11-slim

WORKDIR /app

# System deps for Pillow
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpng-dev libjpeg-dev libfreetype6-dev fonts-dejavu-core \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt requirements-gpu.txt ./
RUN pip install --no-cache-dir -r requirements.txt -r requirements-gpu.txt

COPY . .

ENV MOCK_MODE=false
ENV PYTHONUNBUFFERED=1

CMD ["python", "-m", "src.runpod_handler"]
