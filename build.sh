#!/usr/bin/env bash
# exit on error
set -o errexit

echo "Starting build process..."

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Create data directory with proper permissions
echo "Creating data directory..."
mkdir -p /opt/render/project/src/data
chmod 777 /opt/render/project/src/data

# Initialize database
echo "Initializing database..."
python init_db.py

# Ensure database was created and set permissions
if [ -f /opt/render/project/src/data/store.db ]; then
    echo "Database created successfully"
    chmod 666 /opt/render/project/src/data/store.db
    ls -l /opt/render/project/src/data/store.db
else
    echo "Error: Database file not created"
    exit 1
fi

echo "Build process complete"
