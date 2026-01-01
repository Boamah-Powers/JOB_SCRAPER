#!/bin/bash
set -e  # Exit on any error

# Parse command line arguments
ENV_TYPE="${1:-conda}"  # Default to conda if no argument provided

if [[ "$ENV_TYPE" != "conda" && "$ENV_TYPE" != "venv" ]]; then
    echo "Error: Invalid environment type. Use 'conda' or 'venv'"
    echo "Usage: $0 [conda|venv]"
    exit 1
fi

echo "Setting up scraper with ${ENV_TYPE}..."

# Check if .env exists
if [ ! -f .env ]; then
    echo "Error: .env file not found. Please create it with required credentials."
    exit 1
fi

# Detect OS
OS="$(uname -s)"
case "${OS}" in
    Linux*)     PLATFORM=Linux;;
    Darwin*)    PLATFORM=Mac;;
    CYGWIN*|MINGW*|MSYS*) PLATFORM=Windows;;
    *)          PLATFORM="UNKNOWN:${OS}"
esac

echo "Detected platform: ${PLATFORM}"

# Check for Chrome/Chromium installation
CHROME_FOUND=false
if command -v google-chrome &> /dev/null || command -v chromium &> /dev/null || command -v chromium-browser &> /dev/null; then
    CHROME_FOUND=true
elif [[ "$PLATFORM" == "Mac" ]] && [ -d "/Applications/Google Chrome.app" ]; then
    CHROME_FOUND=true
fi

if [ "$CHROME_FOUND" = false ]; then
    echo "Warning: Chrome/Chromium not found!"
    echo ""
    echo "Please install Chrome for your platform:"
    case "${PLATFORM}" in
        Linux)
            echo "  Ubuntu/Debian: sudo apt-get install -y google-chrome-stable"
            echo "  Fedora/RHEL:   sudo dnf install google-chrome-stable"
            echo "  Arch:          sudo pacman -S google-chrome"
            echo "  Or download from: https://www.google.com/chrome/"
            ;;
        Mac)
            echo "  Using Homebrew: brew install --cask google-chrome"
            echo "  Or download from: https://www.google.com/chrome/"
            ;;
        Windows)
            echo "  Download from: https://www.google.com/chrome/"
            echo "  Or use Chocolatey: choco install googlechrome"
            ;;
    esac
    echo ""
    read -p "Continue without Chrome? (y/N) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Create and activate environment based on type
if [[ "$ENV_TYPE" == "conda" ]]; then
    # Check if conda environment already exists
    if conda env list | grep -q "^scraper "; then
        echo "Conda environment 'scraper' already exists. Activating..."
    else
        echo "Creating conda environment 'scraper'..."
        conda create -n scraper python=3.10 -y
    fi
    
    # Activate conda environment
    eval "$(conda shell.bash hook)"
    conda activate scraper
    
else
    # Python venv
    if [ -d "scraper_env" ]; then
        echo "Virtual environment 'scraper_env' already exists. Activating..."
    else
        echo "Creating Python virtual environment 'scraper_env'..."
        python3 -m venv scraper_env
    fi
    
    # Activate venv
    source scraper_env/bin/activate
fi

# Install Python dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Run the pipeline
python pipeline.py