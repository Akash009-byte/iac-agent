#!/bin/bash

# Step 1-3: Create virtual environment, activate, and install requirements if .venv doesn't exist
if [ ! -d ".venv" ]; then
  echo "Creating virtual environment..."
  python3 -m venv .venv
  echo "Activating virtual environment..."
  source .venv/bin/activate
  echo "Installing requirements..."
  pip install -r requirements.txt
else
  echo "Virtual environment already exists. Activating..."
  source .venv/bin/activate
fi



# Step 4: Navigate to app directory and start the application
cd app/
export OBJC_DISABLE_INITIALIZE_FORK_SAFETY=YES
echo "Starting application with Gunicorn..."
gunicorn -c gunicorn_dev_config.py main:app
