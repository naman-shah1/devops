FROM python:3.9-slim

# Prevent Python from buffering logs
ENV PYTHONUNBUFFERED=1

# Set working directory
WORKDIR /app

# Copy only requirements first (for caching)
COPY app/requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy full app
COPY app/ .

# Expose port
EXPOSE 5000

# Run app
CMD ["python", "app.py"]
