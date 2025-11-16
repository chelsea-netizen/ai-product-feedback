#!/bin/bash
# Script to push updates to GitHub Pages
# Run this after the daily collection completes

cd ~/Desktop/ai_feedback_daily

# Stage all changes
git add -A

# Check if there are changes
if git diff --staged --quiet; then
    echo "No changes to commit"
    exit 0
fi

# Commit with date
DATE=$(date +"%Y-%m-%d")
git commit -m "Update feedback data - $DATE"

echo ""
echo "📤 Ready to push to GitHub!"
echo "To complete the push, please run one of these commands:"
echo ""
echo "Option 1 - Using GitHub CLI (recommended):"
echo "  cd ~/Desktop/ai_feedback_daily"
echo "  gh auth login  # if not already logged in"
echo "  git push origin gh-pages"
echo ""
echo "Option 2 - Open GitHub Desktop:"
echo "  - File → Add Local Repository"
echo "  - Select ~/Desktop/ai_feedback_daily"
echo "  - Click 'Push origin'"
echo ""
