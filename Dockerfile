FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Create directory for sqlite db
RUN mkdir -p /app/data

# Expose ports
EXPOSE 8000
EXPOSE 8501
