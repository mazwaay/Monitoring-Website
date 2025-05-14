FROM python:3.9-slim

# Install dependencies + Chromium
RUN apt-get update && apt-get install -y wget gnupg \
    && playwright install chromium \
    && playwright install-deps

WORKDIR /app
COPY . .
RUN pip install --no-cache-dir -r requirements.txt

CMD ["python", "monitor.py"]