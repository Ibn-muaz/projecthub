#!/usr/bin/env bash
# exit on error
set -o errexit

echo "🚀 Starting deployment..."

# Upgrade pip and install dependencies
pip install --upgrade pip
pip install -r backend/requirements.txt

# Collect static files
echo "📦 Collecting static files..."
python manage.py collectstatic --no-input --clear

# Apply database migrations
echo "🔄 Running migrations..."
python manage.py migrate --no-input

# Populate departments and seed sample projects
echo "📂 Populating departments..."
python manage.py populate_departments
echo "🌱 Seeding sample projects..."
python manage.py seed_projects

echo "✅ Build completed!"
