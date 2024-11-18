# Use an official Python runtime as a parent image
FROM python:3.10-slim

# Set environment variables for Python and Flask
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV FLASK_ENV production

# Set the working directory in the container
WORKDIR /app

# Copy the local application code to the container
COPY . /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Expose the port your Flask app runs on
EXPOSE 5000

# Set the default command to run the application
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "app:app"]
