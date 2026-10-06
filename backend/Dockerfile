FROM python:3.11-slim

WORKDIR /app

# CPU-only PyTorch keeps the image much smaller (sentence-transformers needs torch)
RUN pip install --no-cache-dir torch --index-url https://download.pytorch.org/whl/cpu
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000
# seed.py is safe to run every time: it skips documents that are already indexed
CMD ["sh", "-c", "python scripts/seed.py && uvicorn app.main:app --host 0.0.0.0 --port 8000"]
