#!/bin/bash

echo "📧 Preparing Gmail Spam Detector for GitHub..."
echo "==============================================="

# Check if we're in the right directory
if [ ! -f "gmail_spam_detector.py" ]; then
    echo "❌ Error: Please run this script from the project root directory"
    exit 1
fi

# Initialize git if not already done
if [ ! -d ".git" ]; then
    echo "🔧 Initializing git repository..."
    git init
fi

# Add remote if not exists
if ! git remote get-url origin &> /dev/null; then
    echo "🔗 Adding GitHub remote..."
    git remote add origin https://github.com/scalliontor/Gmail-spam-or-ham.git
fi

# Create .gitignore if it doesn't exist
if [ ! -f ".gitignore" ]; then
    echo "📝 .gitignore not found. Please create it first!"
    exit 1
fi

# Check for sensitive files
echo "🔍 Checking for sensitive files..."
if [ -f "credentials.json" ]; then
    echo "⚠️  WARNING: credentials.json found - make sure it's in .gitignore"
fi

if [ -f "token.json" ]; then
    echo "⚠️  WARNING: token.json found - make sure it's in .gitignore"
fi

# Add files to git
echo "📦 Adding files to git..."
git add .

# Show what will be committed
echo "📋 Files to be committed:"
git status --porcelain

# Commit with timestamp
echo "💾 Committing changes..."
COMMIT_MSG="Updated Gmail Spam Detector - $(date '+%Y-%m-%d %H:%M:%S')"
git commit -m "$COMMIT_MSG"

# Push to GitHub
echo "🚀 Pushing to GitHub..."
git branch -M main
git push -u origin main

echo "✅ Successfully pushed to GitHub!"
echo "🌐 Repository: https://github.com/scalliontor/Gmail-spam-or-ham.git"
echo ""
echo "📌 Important reminders:"
echo "   - credentials.json is excluded from git"
echo "   - Jupyter notebooks are excluded"
echo "   - Users will need to create their own credentials.json"
echo "   - Make sure to update README with setup instructions"
