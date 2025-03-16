#!/usr/bin/env bash
# exit on error
set -o errexit

# Install dependencies
pip install -r requirements.txt

# Create data directory with proper permissions
mkdir -p /opt/render/project/src/data
chmod 777 /opt/render/project/src/data

# Initialize database
python init_db.py

# Set database permissions
chmod 666 /opt/render/project/src/data/store.db
