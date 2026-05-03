#!/bin/bash

echo "🔍 Checking Python..."

if ! command -v python3 &> /dev/null
then
    echo "❌ Python3 not found. Install Python first."
    exit
fi

echo "📦 Installing required packages..."
python3 -m pip install --upgrade pip
python3 -m pip install -r requirements.txt

echo "🚀 Launching app..."
streamlit run ui.py