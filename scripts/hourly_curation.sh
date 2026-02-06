#!/bin/bash
set -e

# Navigate to repo root
cd "$(dirname "$0")/.."

echo "Starting Hourly Curation: $(date)"

# Pull latest
git pull origin main || echo "Git pull failed, continuing anyway..."

# Run curation script
python3 scripts/curate_process.py

# Check for changes
if git diff --quiet s-grade-curated.json; then
    echo "No changes detected."
    exit 0
fi

# Commit and Push
echo "Changes detected. Pushing directly to main."

git add s-grade-curated.json
git commit -m "chore: hourly curation update $(date +%Y-%m-%d)"

# Try pushing
echo "Pushing to remote..."
git push origin main

echo "Done. Direct push complete."
