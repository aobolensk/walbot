#!/bin/sh

echo "-- flake8"
python3 -m flake8 --max-line-length 120 --show-source --exclude venv
echo "-- isort"
python3 -m isort .
echo "-- Lint check is done"
