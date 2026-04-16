FROM python:3.11-slim

WORKDIR /app

# Install dependencies first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# The application files will be mounted at runtime via docker-compose, 
# but copying here ensures the image is self-contained if run directly.
COPY . .

# Expose the API port
EXPOSE 8000

# On container start, apply database migrations then start the server
CMD ["sh", "-c", "alembic upgrade head && uvicorn main:app --host 0.0.0.0 --port 8000"]
