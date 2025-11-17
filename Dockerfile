FROM mcr.microsoft.com/playwright/python:v1.50.0-noble

# System tzdata optional; uncomment if you want correct logs
# RUN apt-get update && apt-get install -y tzdata && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . ./app/
EXPOSE 8080
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]
