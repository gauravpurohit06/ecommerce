# syntax=docker/dockerfile:1

############################
# Stage 1: Testing
############################
FROM python:3.11-slim AS test

# Prevent Python from writing .pyc files
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Install production dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install pytest for testing
RUN pip install --no-cache-dir pytest

# Copy application code
COPY . .

# Run integration tests
RUN pytest tests/

############################
# Stage 2: Production
############################
FROM python:3.11-slim AS prod

# Prevent Python from writing .pyc files
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Install production dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose the application's port (adjust if different)
EXPOSE 8002

# Start the application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8002", "--log-config", "log_config.yaml"]
