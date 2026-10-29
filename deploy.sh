#!/bin/bash

# Spatial Intelligence Survey Website - GitHub Pages Deployment Script
# Usage: ./deploy.sh "commit message"

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}================================${NC}"
echo -e "${BLUE}Deploying to GitHub Pages${NC}"
echo -e "${BLUE}================================${NC}\n"

# Check if git is initialized
if [ ! -d .git ]; then
    echo -e "${YELLOW}Git repository not initialized. Initializing now...${NC}"
    git init
    echo -e "${GREEN}✓ Git initialized${NC}\n"
fi

# Get commit message from argument or use default
COMMIT_MSG="${1:-Update website}"

# Stage all changes
echo -e "${BLUE}Staging changes...${NC}"
git add .

# Show what will be committed
echo -e "\n${BLUE}Files to be committed:${NC}"
git status --short

# Commit changes
echo -e "\n${BLUE}Committing changes...${NC}"
git commit -m "$COMMIT_MSG"

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Changes committed${NC}\n"
else
    echo -e "${YELLOW}No changes to commit or commit failed${NC}\n"
fi

# Check if remote exists
if ! git remote | grep -q origin; then
    echo -e "${RED}Error: No remote 'origin' configured${NC}"
    echo -e "${YELLOW}Please add a remote first:${NC}"
    echo -e "  git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git"
    exit 1
fi

# Push to GitHub
echo -e "${BLUE}Pushing to GitHub...${NC}"
git push origin main

if [ $? -eq 0 ]; then
    echo -e "\n${GREEN}================================${NC}"
    echo -e "${GREEN}✓ Deployment successful!${NC}"
    echo -e "${GREEN}================================${NC}\n"
    echo -e "Your site will be available at:"
    echo -e "${BLUE}https://YOUR_USERNAME.github.io/YOUR_REPO/${NC}\n"
    echo -e "Note: It may take a few minutes for changes to appear.\n"
else
    echo -e "\n${RED}✗ Push failed${NC}"
    echo -e "${YELLOW}Please check your remote configuration and try again${NC}\n"
    exit 1
fi
