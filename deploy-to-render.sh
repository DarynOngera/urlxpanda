#!/bin/bash

# URLXpanda - Deploy to Render Script
# This script helps you commit and push changes for Render deployment

set -e

echo "🚀 URLXpanda - Render Deployment Helper"
echo "========================================"
echo ""

# Check if git is installed
if ! command -v git &> /dev/null; then
    echo "❌ Error: git is not installed"
    exit 1
fi

# Check if we're in a git repository
if ! git rev-parse --git-dir > /dev/null 2>&1; then
    echo "❌ Error: Not in a git repository"
    exit 1
fi

echo "📋 Files to be committed:"
echo "  - render.yaml (updated)"
echo "  - DEPLOYMENT.md (updated)"
echo "  - Dockerfile (new)"
echo "  - .dockerignore (new)"
echo "  - RAILWAY_TO_RENDER_MIGRATION.md (new)"
echo "  - RENDER_QUICKSTART.md (new)"
echo "  - MIGRATION_SUMMARY.md (new)"
echo ""

# Show git status
echo "📊 Current git status:"
git status --short
echo ""

# Ask for confirmation
read -p "Do you want to commit these changes? (y/n) " -n 1 -r
echo ""

if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "❌ Aborted"
    exit 1
fi

# Add files
echo "📦 Adding files..."
git add render.yaml
git add DEPLOYMENT.md
git add Dockerfile
git add .dockerignore
git add RAILWAY_TO_RENDER_MIGRATION.md
git add RENDER_QUICKSTART.md
git add MIGRATION_SUMMARY.md
git add deploy-to-render.sh

# Commit
echo "💾 Committing changes..."
git commit -m "Configure Render deployment and migration from Railway

- Enhanced render.yaml with health checks and auto-deploy
- Added comprehensive migration documentation
- Created Dockerfile for optional Docker deployment
- Updated DEPLOYMENT.md with Render instructions
- Added quick start guide for 5-minute deployment"

echo "✅ Changes committed successfully!"
echo ""

# Ask about pushing
read -p "Do you want to push to GitHub now? (y/n) " -n 1 -r
echo ""

if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "🚀 Pushing to GitHub..."
    
    # Get current branch
    BRANCH=$(git rev-parse --abbrev-ref HEAD)
    
    # Push
    git push origin "$BRANCH"
    
    echo "✅ Pushed to GitHub successfully!"
    echo ""
    echo "🎉 Next Steps:"
    echo "1. Go to https://render.com"
    echo "2. Click 'New +' → 'Blueprint'"
    echo "3. Select your repository"
    echo "4. Click 'Apply'"
    echo ""
    echo "📚 For detailed instructions, see:"
    echo "   - RENDER_QUICKSTART.md (quick 5-min guide)"
    echo "   - RAILWAY_TO_RENDER_MIGRATION.md (detailed migration)"
    echo "   - MIGRATION_SUMMARY.md (overview)"
else
    echo "⏸️  Changes committed but not pushed"
    echo ""
    echo "To push later, run:"
    echo "  git push origin $(git rev-parse --abbrev-ref HEAD)"
fi

echo ""
echo "✨ Done!"
