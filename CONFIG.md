# Website Configuration Guide

This file provides a quick reference for customizing the Spatial Intelligence Survey website.

## Quick Links to Update

### 1. Main Links (index.html)

**Hero Section CTA Buttons** (Lines ~17-27):
- PDF Link: `href="YOUR_PDF_URL"`
- GitHub Link: `href="YOUR_GITHUB_URL"`
- arXiv Link: `href="YOUR_ARXIV_URL"`

**Footer Links** (Lines ~242-246):
- Same as above + email contact

### 2. Meta Information (index.html, Lines ~30-40)

```html
<div class="meta-item">
    <span>📅</span>
    <span>Last Updated: [YOUR_DATE]</span>
</div>
<div class="meta-item">
    <span>📖</span>
    <span>[NUMBER]+ Pages</span>
</div>
<div class="meta-item">
    <span>📚</span>
    <span>[NUMBER]+ References</span>
</div>
```

### 3. Statistics (index.html, Lines ~56-73)

Update the four stat cards:
- Number of Chapters
- Number of Parts
- Number of References
- Number of Application Domains

### 4. Citation (index.html, Lines ~200-208)

Replace with actual BibTeX:
```bibtex
@book{spatial_intelligence_2026,
  title     = {Spatial Intelligence: A Comprehensive Survey},
  author    = {[AUTHOR NAMES]},
  year      = {2026},
  publisher = {[PUBLISHER]},
  note      = {Available at [URL]}
}
```

### 5. Authors (index.html, Lines ~220-237)

Add one card per author:
```html
<div class="author-card">
    <div class="author-avatar">[INITIALS]</div>
    <div class="author-name">[FULL NAME]</div>
    <div class="author-affiliation">[INSTITUTION]</div>
</div>
```

## Color Scheme Customization (styles.css)

### Primary Colors (Lines ~7-18)
```css
:root {
    --bg-primary: #FAF8F5;      /* Page background */
    --bg-secondary: #F5EFE6;    /* Section background */
    --bg-card: #FFFFFF;         /* Card background */
    --text-primary: #2B1D14;    /* Main text */
    --text-secondary: #5C3D2E;  /* Secondary text */
    --text-muted: #8B7355;      /* Muted text */
    --accent: #B96420;          /* Accent color */
    --accent-hover: #A05518;    /* Accent hover */
    --border: #E5DED3;          /* Border color */
}
```

### Background Pattern (Lines ~30-40)
Adjust hexagon pattern size:
```css
background-size: 80px 140px;  /* Change these values */
```

## Content Updates

### Book Structure (Lines ~90-180)
Each part has:
- Part number (I-V)
- Title
- Description
- Chapter list

### Features (Lines ~185-225)
Six feature cards with:
- Icon (emoji)
- Title
- Description

## SEO & Meta Tags (index.html, Lines ~4-9)

```html
<meta name="description" content="[YOUR DESCRIPTION]">
<meta name="keywords" content="[YOUR KEYWORDS]">
<meta name="author" content="[YOUR NAME]">
<title>[YOUR TITLE]</title>
```

## Social Media Preview (Optional)

Add Open Graph tags in `<head>`:

```html
<!-- Open Graph / Facebook -->
<meta property="og:type" content="website">
<meta property="og:url" content="YOUR_URL">
<meta property="og:title" content="Spatial Intelligence: A Comprehensive Survey">
<meta property="og:description" content="YOUR_DESCRIPTION">
<meta property="og:image" content="YOUR_IMAGE_URL">

<!-- Twitter -->
<meta property="twitter:card" content="summary_large_image">
<meta property="twitter:url" content="YOUR_URL">
<meta property="twitter:title" content="Spatial Intelligence: A Comprehensive Survey">
<meta property="twitter:description" content="YOUR_DESCRIPTION">
<meta property="twitter:image" content="YOUR_IMAGE_URL">
```

## Adding Images

To add images (book cover, diagrams, etc.):

1. Create an `images/` folder
2. Add images there
3. Reference in HTML:
   ```html
   <img src="images/cover.jpg" alt="Book Cover">
   ```

## Optional Enhancements

### Add Favicon
```html
<link rel="icon" type="image/png" href="favicon.png">
```

### Add Google Analytics
```html
<!-- Before </head> -->
<script async src="https://www.googletagmanager.com/gtag/js?id=YOUR_GA_ID"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){dataLayer.push(arguments);}
  gtag('js', new Date());
  gtag('config', 'YOUR_GA_ID');
</script>
```

### Add Download Button
```html
<a href="path/to/book.pdf" download class="btn btn-primary">
    📥 Download PDF
</a>
```

## Testing Checklist

- [ ] All links work correctly
- [ ] Citation can be copied
- [ ] Responsive on mobile devices
- [ ] Smooth scrolling works
- [ ] Animations trigger properly
- [ ] No console errors
- [ ] Fast loading time

## Deployment Checklist

- [ ] Updated all placeholder links
- [ ] Added real author information
- [ ] Updated citation with correct details
- [ ] Verified meta tags for SEO
- [ ] Tested on multiple browsers
- [ ] Optimized images (if added)
- [ ] Set up GitHub Pages
- [ ] Added custom domain (optional)

---

For detailed instructions, see README.md
