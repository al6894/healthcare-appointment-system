# Use the official Python image as the base image
FROM python:3.12-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install dependencies, including distutils
RUN apt-get update && apt-get install -y \
    python3-distutils python3-pip && \
    pip3 install --no-cache-dir --upgrade pip

# Set the working directory in the container
WORKDIR /app

# Copy only requirements first (leverage Docker caching)
COPY requirements.txt /app/

# Install dependencies
RUN pip3 install --no-cache-dir -r requirements.txt

# Copy application code to the container
COPY . /app

# Expose the port Flask runs on
EXPOSE 5000

# Command to run the app
CMD ["sh", "-c", "python src/provider_service/app.py"]