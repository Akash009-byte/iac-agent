# Use Python 3.9 slim as the base image
FROM python:3.9-slim AS base

# Set the working directory inside the container
WORKDIR /app

# Copy only the requirements file to leverage Docker cache
COPY requirements.txt .

# Install the dependencies
RUN pip install -r requirements.txt

# Copy the entire application code to the container
COPY . .

# Set the working directory to the app folder
WORKDIR /app/app

# Set environment variable
ENV OBJC_DISABLE_INITIALIZE_FORK_SAFETY=YES

# Command to run the application using gunicorn with external config
CMD ["gunicorn", "-c", "gunicorn_prod_config.py", "main:app"]
