# Member 3 – AI Skin Disease Classification (TensorFlow)
FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
ENV PYTHONPATH=/app
EXPOSE 8002

# Run API from project root so api.main can import src
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8002"]
