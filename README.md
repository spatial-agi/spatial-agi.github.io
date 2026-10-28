# Spatial Intelligence Survey Website

Official website for the Spatial Intelligence: A Comprehensive Survey 2026 book.

> **Note**: This website uses a clean, immediate-display design with no scroll-triggered animations. All content is visible immediately on page load for better accessibility and user experience.

## 🚀 Quick Start

### View Locally

Simply open `index.html` in your web browser:

```bash
open index.html
```

Or use a local server (recommended):

```bash
# Python 3
python -m http.server 8000

# Python 2
python -m SimpleHTTPServer 8000

# Node.js (if you have http-server installed)
npx http-server

# VS Code Live Server extension
# Right-click index.html → "Open with Live Server"
```

Then visit `http://localhost:8000` in your browser.

### Deploy to GitHub Pages

1. **Create a GitHub repository** for your project

2. **Push the website files**:
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git branch -M main
   git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git
   git push -u origin main
   ```

3. **Enable GitHub Pages**:
   - Go to your repository on GitHub
   - Navigate to Settings → Pages
   - Under "Source", select "main" branch and "/ (root)" folder
   - Click "Save"
   - Your site will be live at `https://YOUR_USERNAME.github.io/YOUR_REPO/`

## 📁 File Structure

```
website/
├── index.html      # Main HTML structure
├── styles.css      # All styling and layout
├── script.js       # Interactive features
└── README.md       # This file
```

## ✏️ Customization Guide

### 1. Update Links

In `index.html`, replace placeholder links with actual URLs:

```html
<!-- Line ~17-27: CTA buttons -->
<a href="YOUR_PDF_URL" class="btn btn-primary">📄 Read the Book</a>
<a href="YOUR_GITHUB_URL" class="btn btn-secondary">💻 GitHub</a>
<a href="YOUR_ARXIV_URL" class="btn btn-secondary">📊 arXiv</a>

<!-- Line ~242-246: Footer links -->
<a href="YOUR_GITHUB_URL" class="footer-link">GitHub</a>
<a href="YOUR_ARXIV_URL" class="footer-link">arXiv</a>
<a href="mailto:YOUR_EMAIL" class="footer-link">Contact</a>
```

### 2. Update Citation

In `index.html`, line ~200-208, update the BibTeX citation:

```bibtex
@book{spatial_intelligence_2026,
  title     = {Spatial Intelligence: A Comprehensive Survey},
  author    = {Your Name and Co-authors},
  year      = {2026},
  publisher = {Your Publisher},
  note      = {Available at https://github.com/your-repo}
}
```

### 3. Add Authors

In `index.html`, line ~220-237, add author cards:

```html
<div class="author-card">
    <div class="author-avatar">AB</div>
    <div class="author-name">Author Name</div>
    <div class="author-affiliation">University Name</div>
</div>
```

### 4. Update Statistics

In `index.html`, line ~56-73, modify stats if needed:

```html
<div class="stat-number">17</div>
<div class="stat-label">Chapters</div>
```

### 5. Customize Colors

In `styles.css`, line ~7-18, modify CSS variables:

```css
:root {
    --accent: #B96420;         /* Main accent color */
    --accent-hover: #A05518;   /* Hover state */
    --bg-primary: #FAF8F5;     /* Page background */
    /* ... other variables ... */
}
```

### 6. Update Content

Edit chapter lists, descriptions, and features directly in `index.html`:
- **Part descriptions**: Lines ~90-180
- **Features**: Lines ~185-225
- **Meta information**: Lines ~30-40

## 🎨 Design Features

- ✅ Responsive design (mobile, tablet, desktop)
- ✅ Animated hexagonal background pattern
- ✅ Smooth scroll animations
- ✅ Interactive hover effects
- ✅ Copy-to-clipboard for citation
- ✅ Progress bar indicator
- ✅ Parallax hero section
- ✅ Accessible and SEO-friendly

## 🔧 Browser Support

- Chrome/Edge (latest)
- Firefox (latest)
- Safari (latest)
- Mobile browsers (iOS Safari, Chrome Mobile)

## 📝 License

Update the footer in `index.html` with your preferred license.

## 🤝 Contributing

To contribute to the website:

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Open a Pull Request

## 📧 Contact

For questions or suggestions, please open an issue on GitHub or contact the authors.

---

**Last Updated**: October 2026
