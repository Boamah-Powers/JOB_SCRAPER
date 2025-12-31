#!/bin/bash
set -e  # Exit on any error

# Check if .env exists
if [ ! -f .env ]; then
    echo "Error: .env file not found. Please create it with required credentials."
    exit 1
fi

# Install system dependencies (Ubuntu/Debian)
if ! command -v google-chrome &> /dev/null; then
    echo "Chrome not found. Installing..."
    wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | sudo apt-key add -
    sudo sh -c 'echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list'
    sudo apt-get update
    sudo apt-get install -y google-chrome-stable
fi

# Create and activate virtual environment
python3 -m venv scraper_env
source scraper_env/bin/activate

# Install Python dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Run the pipeline
python pipeline.py