#!/usr/bin/env bash
set -euo pipefail

# Render build script for Django app deployment.
# Installs dependencies and collects static assets for WhiteNoise.
python -m pip install --upgrade pip
pip install -r requirements.txt
python manage.py collectstatic --noinput
