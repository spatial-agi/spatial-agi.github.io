# Changelog

## 2026-10-26 - Initial Release + Animation Update

### ✅ Removed (Per User Request)
- ❌ Removed scroll-triggered fade-in animations on cards
- ❌ Removed parallax effect on hero section
- ❌ Removed keyframe animation definitions

### ✅ Kept Features
- ✓ Smooth scrolling for anchor links
- ✓ Copy-to-clipboard for citation
- ✓ Scroll progress indicator (top bar)
- ✓ Hover effects on cards and buttons
- ✓ All responsive design features

### 📊 Result
**Before**: Content fades in as you scroll
**After**: All content displays immediately, no delayed animations

### 🎯 Current Behavior
- All sections are immediately visible on page load
- No opacity transitions when scrolling
- Cards and buttons still have hover effects
- Smooth scrolling still works for navigation
- Progress bar still shows scroll position

### 📝 File Changes
- `script.js`: Reduced from 126 lines to 91 lines (-35 lines)
  - Removed IntersectionObserver code
  - Removed parallax scroll handler
- `styles.css`: Removed animation keyframes and classes
  - Removed `@keyframes fadeInUp`
  - Removed `.fade-in-up` class

### 💾 File Sizes (After Update)
- script.js: ~3 KB (was ~4 KB)
- styles.css: ~8.5 KB (was ~9 KB)
- Total reduction: ~1.5 KB

---

## Original Features

### Core Functionality
1. **Responsive Design** - Works on all devices
2. **Smooth Navigation** - Click links to smoothly scroll to sections
3. **Citation Copy** - Click button to copy BibTeX citation
4. **Scroll Progress** - Top bar shows reading progress
5. **Hover Effects** - Interactive feedback on all clickable elements

### Design Elements
- Warm color palette (orange-brown tones)
- Hexagonal background pattern
- Card-based layout
- Clean typography
- Professional appearance

### Technical Details
- Pure HTML/CSS/JavaScript
- No frameworks or dependencies
- GitHub Pages ready
- SEO optimized
- Fast loading (~45 KB total)

---

## Future Updates

Possible enhancements (not yet implemented):
- [ ] Dark mode toggle
- [ ] Search functionality
- [ ] Table of contents sidebar
- [ ] Back-to-top button
- [ ] Social sharing buttons
- [ ] Print-friendly stylesheet
