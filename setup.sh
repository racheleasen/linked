#!/bin/bash

echo "Starting environment setup..."

# --- Virtual Environment ---
if [ ! -d "venv" ]; then
  echo "📦 Creating virtual environment..."
  python3 -m venv venv || { echo "❌ Failed to create virtual environment"; exit 1; }
fi

echo "📦 Activating virtual environment..."
source venv/bin/activate

# --- Install Dependencies ---
echo "📚 Installing Python packages..."
pip install --upgrade pip
pip install -r requirements.txt || { echo "❌ pip install failed"; exit 1; }

# --- GazeTracking Setup ---
GAZE_DIR="gaze/base"
if [ ! -d "$GAZE_DIR" ]; then
  echo "👁️ Cloning GazeTracking into $GAZE_DIR..."
  mkdir -p "$(dirname "$GAZE_DIR")"
  git clone https://github.com/antoinelame/GazeTracking.git "$GAZE_DIR" || {
    echo "❌ Failed to clone GazeTracking"
    exit 1
  }
else
  echo "✅ GazeTracking already exists at $GAZE_DIR"
fi

# --- Data Directories ---
echo "📂 Ensuring user folders exist..."
mkdir -p data

echo "✅ Setup complete!"
