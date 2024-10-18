# Use the official Python image from the Docker Hub as the base image
FROM python:3.10-slim

# Set environment variables to prevent Python from writing .pyc files and buffering stdout/stderr
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set the working directory inside the container
WORKDIR /app

# Install system dependencies
# These are necessary for some Python packages (e.g., aiohttp, pytz)
RUN apt-get update && \
    apt-get install -y --no-install-recommends gcc build-essential && \
    rm -rf /var/lib/apt/lists/*

# Copy the requirements.txt file to the working directory
COPY requirements.txt .

# Upgrade pip and install Python dependencies
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code to the working directory
COPY . .

# (Optional) Create a non-root user for security best practices
# It's recommended to run containers as non-root users to minimize security risks
RUN useradd -m sydneybot && \
    chown -R sydneybot:sydneybot /app

# Switch to the non-root user
USER sydneybot

# Define the command to run the bot
CMD ["python", "bot.py"]