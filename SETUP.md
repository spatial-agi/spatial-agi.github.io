# 🚀 Quick Setup Guide

Get your Spatial Intelligence Survey website live on GitHub Pages in 5 minutes!

## ⚡ Fast Track (3 Steps)

### 1️⃣ Preview Locally

```bash
cd website
./preview.sh
# Visit http://localhost:8000
```

### 2️⃣ Update Your Info

Edit `index.html` and replace:
- `YOUR_PDF_URL` → Link to your book PDF
- `YOUR_GITHUB_URL` → Your GitHub repository URL
- `YOUR_ARXIV_URL` → Your arXiv paper URL (if available)
- `[Authors]` → Your author names in the citation section

### 3️⃣ Deploy to GitHub Pages

```bash
# First time only: Create GitHub repo and connect it
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git

# Deploy (every time you make changes)
./deploy.sh "Initial deployment"
```

Then enable GitHub Pages:
- Go to your repo → Settings → Pages
- Source: `main` branch, `/ (root)` folder
- Click Save

**Done!** Your site will be live at `https://YOUR_USERNAME.github.io/YOUR_REPO/`

---

## 📝 Detailed Setup

### Prerequisites

- Git installed
- GitHub account
- Text editor (VS Code, Sublime, etc.)

### Step-by-Step

#### 1. Create GitHub Repository

1. Go to https://github.com/new
2. Repository name: `spatial-intelligence-survey` (or your choice)
3. Public or Private (Public for GitHub Pages free tier)
4. Don't initialize with README (we have files already)
5. Click "Create repository"

#### 2. Connect Your Local Repository

```bash
cd website

# Initialize git (if not done)
git init

# Add your remote
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git

# Verify
git remote -v
```

#### 3. Customize Content

**Minimum required changes:**

- [ ] PDF/GitHub/arXiv links in hero section
- [ ] Author information in citation
- [ ] Author cards at bottom

**Optional changes:**

- [ ] Update statistics (chapters, references, etc.)
- [ ] Modify chapter descriptions
- [ ] Change color scheme
- [ ] Add your logo/images

See `CONFIG.md` for detailed customization guide.

#### 4. Test Locally

```bash
# Start preview server
./preview.sh

# Or manually
python3 -m http.server 8000
```

Visit http://localhost:8000 and check:
- All links work
- Content displays correctly
- Mobile responsive (resize browser)
- No console errors (F12 DevTools)

#### 5. Deploy

```bash
# First deployment
git add .
git commit -m "Initial website deployment"
git branch -M main
git push -u origin main

# Or use the script
./deploy.sh "Initial deployment"
```

#### 6. Enable GitHub Pages

1. Go to your repository on GitHub
2. Click **Settings** tab
3. Scroll to **Pages** section (left sidebar)
4. Under **Source**:
   - Branch: `main`
   - Folder: `/ (root)`
   - Click **Save**
5. Wait 2-3 minutes
6. Your site is live! URL will show at the top of Pages settings

### 🎉 Success!

Your website is now live at:
```
https://YOUR_USERNAME.github.io/YOUR_REPO/
```

---

## 🔄 Making Updates

Whenever you want to update content:

```bash
# 1. Edit files (index.html, etc.)

# 2. Preview locally
./preview.sh

# 3. Deploy
./deploy.sh "Update chapter descriptions"
```

Changes appear on GitHub Pages in 1-2 minutes.

---

## 🎨 Customization Quick Reference

### Change Colors
Edit `styles.css`, lines 7-18:
```css
:root {
    --accent: #B96420;  /* Your brand color */
}
```

### Add Authors
Edit `index.html`, lines 220-237:
```html
<div class="author-card">
    <div class="author-avatar">YZ</div>
    <div class="author-name">Your Name</div>
    <div class="author-affiliation">Your Institution</div>
</div>
```

### Update Stats
Edit `index.html`, lines 56-73:
```html
<div class="stat-number">17</div>
<div class="stat-label">Chapters</div>
```

---

## 🆘 Troubleshooting

### "Remote origin already exists"
```bash
git remote remove origin
git remote add origin YOUR_NEW_URL
```

### "Permission denied (publickey)"
Use HTTPS instead of SSH:
```bash
git remote set-url origin https://github.com/USER/REPO.git
```

### "Site not showing after deployment"
- Wait 2-3 minutes for GitHub Pages to build
- Check Settings → Pages for any errors
- Ensure branch is set to `main` and folder to `/ (root)`
- Check Actions tab for build status

### "404 Not Found on GitHub Pages"
- Verify `index.html` exists in root directory
- Check repository is public (or you have GitHub Pro)
- Wait a few more minutes

---

## 📚 More Resources

- Full documentation: See `README.md`
- Customization guide: See `CONFIG.md`
- GitHub Pages docs: https://pages.github.com/
- Git basics: https://git-scm.com/doc

---

## 💡 Pro Tips

1. **Custom Domain**: You can add your own domain in Settings → Pages → Custom domain
2. **HTTPS**: Automatically enabled for `.github.io` domains
3. **Analytics**: Add Google Analytics code to track visitors (see CONFIG.md)
4. **SEO**: Update meta tags in `<head>` section (see CONFIG.md)

---

**Need help?** Check the README.md or open an issue on GitHub!
