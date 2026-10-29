# 📁 Website Files Overview

## Core Website Files

### `index.html` (11KB)
Main HTML structure containing all content:
- Hero section with title, description, CTA buttons
- Overview and statistics
- Book structure (5 parts with chapters)
- Key features section
- Citation (BibTeX)
- Authors section
- Footer

**What to customize:**
- Links (PDF, GitHub, arXiv)
- Author information
- Citation details
- Statistics numbers

---

### `styles.css` (9KB)
Complete styling and layout:
- CSS variables for easy color customization
- Responsive grid layouts
- Hexagonal background pattern
- Card styles with hover effects
- Typography and spacing
- Mobile responsive breakpoints

**What to customize:**
- Color scheme (lines 7-18)
- Background pattern size (lines 30-40)
- Font sizes if needed

---

### `script.js` (4KB)
Interactive features:
- Smooth scrolling
- Fade-in animations on scroll
- Copy citation button
- Scroll progress bar
- Parallax hero effect

**Usually no changes needed**

---

## Documentation Files

### `README.md` (4KB)
Comprehensive documentation:
- Quick start instructions
- File structure explanation
- Customization guide
- Deployment instructions
- Browser support info

**For reference and GitHub display**

---

### `SETUP.md` (New!)
Step-by-step setup guide:
- Fast track (3 steps)
- Detailed walkthrough
- GitHub Pages configuration
- Troubleshooting tips
- Customization quick reference

**Start here if you're new to GitHub Pages**

---

### `CONFIG.md` (5KB)
Detailed customization reference:
- Line numbers for quick edits
- All customization points
- Color scheme guide
- SEO optimization
- Optional enhancements

**Use when making specific changes**

---

## Utility Files

### `deploy.sh` (Executable script)
Automated deployment script:
```bash
./deploy.sh "Your commit message"
```
- Stages all changes
- Commits with your message
- Pushes to GitHub
- Shows deployment status

**Usage:** Run after making changes

---

### `preview.sh` (Executable script)
Local preview server:
```bash
./preview.sh
```
- Starts HTTP server on port 8000
- Opens http://localhost:8000
- Works with Python or Node.js

**Usage:** Run before deploying to test changes

---

### `.gitignore`
Prevents unwanted files from being committed:
- OS files (.DS_Store, Thumbs.db)
- Editor files (.vscode, .idea)
- Logs and temporary files

**Usually no changes needed**

---

## Suggested Workflow

### First Time Setup
1. Read `SETUP.md` (fast track section)
2. Edit `index.html` (update links and authors)
3. Run `./preview.sh` to test locally
4. Create GitHub repo
5. Run `./deploy.sh "Initial commit"`
6. Enable GitHub Pages in repo settings

### Making Updates
1. Edit files (`index.html`, `styles.css`, etc.)
2. Run `./preview.sh` to test
3. Run `./deploy.sh "Description of changes"`
4. Wait 2-3 minutes for GitHub Pages to update

### Reference When Needed
- `README.md` - General documentation
- `CONFIG.md` - Specific customization help
- `SETUP.md` - Setup and troubleshooting

---

## File Size Summary
```
index.html   - 11 KB   [Main content]
styles.css   - 9 KB    [All styling]
script.js    - 4 KB    [Interactivity]
README.md    - 4 KB    [Documentation]
CONFIG.md    - 5 KB    [Customization guide]
SETUP.md     - 6 KB    [Setup guide]
deploy.sh    - 2 KB    [Deploy script]
preview.sh   - 1 KB    [Preview script]
.gitignore   - 1 KB    [Git config]
-----------------------------------
Total:       ~43 KB    [Very lightweight!]
```

---

## Quick Customization Checklist

- [ ] **index.html** line 17-27: Update CTA button links
- [ ] **index.html** line 30-40: Update meta information
- [ ] **index.html** line 200-208: Update citation
- [ ] **index.html** line 220-237: Add author cards
- [ ] **index.html** line 242-246: Update footer links
- [ ] **styles.css** line 7-18: Customize colors (optional)
- [ ] Test with `./preview.sh`
- [ ] Deploy with `./deploy.sh "Initial deployment"`

---

## Support

- Questions? See `README.md`
- Setup help? See `SETUP.md`
- Customization? See `CONFIG.md`
- Issues? Open an issue on GitHub

---

**Last Updated**: October 26, 2026
