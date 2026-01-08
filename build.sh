#!/usr/bin/env bash
# exit on error
set -o errexit

# Install setuptools first (required for drf-yasg on Python 3.12+)
pip install --upgrade pip setuptools

# Install dependencies
pip install -r backend/requirements.txt

# Collect static files
python manage.py collectstatic --no-input

# Run migrations
python manage.py migrate
