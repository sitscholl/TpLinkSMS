FROM mcr.microsoft.com/playwright/python:latest

# System tzdata optional; uncomment if you want correct logs
# RUN apt-get update && apt-get install -y tzdata && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8080
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
