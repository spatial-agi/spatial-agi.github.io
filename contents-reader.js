// ============================================
// Book Reader Navigation and Interaction
// ============================================

document.addEventListener('DOMContentLoaded', function() {
    initBookReader();
});

function initBookReader() {
    // Initialize TOC navigation
    initTOCNavigation();

    // Initialize section navigation
    initSectionNavigation();

    // Initialize sidebar toggle for mobile
    initSidebarToggle();

    // Initialize scroll spy
    initScrollSpy();

    // Load initial section from URL hash
    loadSectionFromHash();
}

// ============================================
// Table of Contents Navigation
// ============================================

function initTOCNavigation() {
    // Part and chapter toggles
    const tocToggles = document.querySelectorAll('.toc-toggle');

    tocToggles.forEach(toggle => {
        toggle.addEventListener('click', function(e) {
            e.preventDefault();
            e.stopPropagation();

            const isActive = this.classList.contains('active');
            const chapters = this.nextElementSibling;

            if (chapters && (chapters.classList.contains('toc-chapters') ||
                             chapters.classList.contains('toc-sections'))) {

                if (isActive) {
                    this.classList.remove('active');
                    chapters.style.display = 'none';
                    const icon = this.querySelector('.toggle-icon');
                    if (icon) icon.textContent = '▶';
                } else {
                    this.classList.add('active');
                    chapters.style.display = 'block';
                    const icon = this.querySelector('.toggle-icon');
                    if (icon) icon.textContent = '▼';
                }
            }
        });
    });

    // TOC links - section navigation
    const tocLinks = document.querySelectorAll('.toc-link');

    tocLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();

            // Get target section
            const targetId = this.getAttribute('href').substring(1);
            const sectionId = this.dataset.section;

            // Navigate to section
            navigateToSection(sectionId || targetId);

            // Update active state
            updateActiveTOCLink(this);

            // Close sidebar on mobile
            if (window.innerWidth <= 768) {
                closeSidebar();
            }
        });
    });
}

function navigateToSection(sectionId) {
    // Hide all sections
    const sections = document.querySelectorAll('.content-section');
    sections.forEach(section => {
        section.classList.remove('active');
    });

    // Show target section
    const targetSection = document.getElementById(sectionId);
    if (targetSection) {
        targetSection.classList.add('active');

        // Scroll to top of content area
        const contentArea = document.getElementById('contentArea');
        contentArea.scrollTop = 0;

        // Update URL hash
        history.pushState(null, '', '#' + sectionId);

        // Update page title
        const heading = targetSection.querySelector('h1, h2');
        if (heading) {
            document.title = heading.textContent + ' - Spatial Intelligence Survey';
        }
    }
}

function updateActiveTOCLink(activeLink) {
    // Remove active class from all links
    const allLinks = document.querySelectorAll('.toc-link');
    allLinks.forEach(link => link.classList.remove('active'));

    // Add active class to clicked link
    activeLink.classList.add('active');

    // Expand parent sections
    let parent = activeLink.parentElement;
    while (parent && parent !== document.querySelector('.toc-nav')) {
        if (parent.classList.contains('toc-chapters') ||
            parent.classList.contains('toc-sections')) {
            parent.style.display = 'block';

            const toggle = parent.previousElementSibling;
            if (toggle && toggle.classList.contains('toc-toggle')) {
                toggle.classList.add('active');
                const icon = toggle.querySelector('.toggle-icon');
                if (icon) icon.textContent = '▼';
            }
        }
        parent = parent.parentElement;
    }
}

// ============================================
// Section Navigation (Previous/Next)
// ============================================

function initSectionNavigation() {
    const navLinks = document.querySelectorAll('.nav-prev, .nav-next');

    navLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            const targetId = this.getAttribute('href').substring(1);
            navigateToSection(targetId);

            // Update TOC active state
            const tocLink = document.querySelector(`.toc-link[data-section="${targetId}"]`);
            if (tocLink) {
                updateActiveTOCLink(tocLink);
            }
        });
    });
}

// ============================================
// Sidebar Toggle for Mobile
// ============================================

function initSidebarToggle() {
    const sidebarToggle = document.getElementById('sidebarToggle');
    const sidebar = document.getElementById('sidebar');

    if (sidebarToggle && sidebar) {
        sidebarToggle.addEventListener('click', function() {
            sidebar.classList.toggle('open');
        });
    }
}

function closeSidebar() {
    const sidebar = document.getElementById('sidebar');
    if (sidebar) {
        sidebar.classList.remove('open');
    }
}

// ============================================
// Scroll Spy (Optional)
// ============================================

function initScrollSpy() {
    // This would track which section is visible in the content area
    // and update the TOC accordingly
    // Implementation depends on your specific needs
}

// ============================================
// Load Section from URL Hash
// ============================================

function loadSectionFromHash() {
    const hash = window.location.hash.substring(1);

    if (hash) {
        // Find and activate the section
        const section = document.getElementById(hash);
        if (section) {
            navigateToSection(hash);

            // Find and activate corresponding TOC link
            const tocLink = document.querySelector(`.toc-link[data-section="${hash}"]`) ||
                           document.querySelector(`.toc-link[href="#${hash}"]`);
            if (tocLink) {
                updateActiveTOCLink(tocLink);
            }
        }
    } else {
        // Show first section by default (preface)
        navigateToSection('preface');
        const firstLink = document.querySelector('.toc-link[data-section="preface"]');
        if (firstLink) {
            updateActiveTOCLink(firstLink);
        }
    }
}

// Listen for hash changes (back/forward navigation)
window.addEventListener('hashchange', function() {
    loadSectionFromHash();
});

// ============================================
// Search Functionality (Optional Enhancement)
// ============================================

function initBookSearch() {
    // This could implement a search feature for the book content
    // You could use a library like Fuse.js for client-side search
}

// ============================================
// Reading Progress Tracker (Optional)
// ============================================

function initReadingProgress() {
    // Track how far the user has read in each section
    // Could store in localStorage
}

// ============================================
// Keyboard Navigation
// ============================================

document.addEventListener('keydown', function(e) {
    // Arrow keys for navigation
    if (e.altKey) {
        if (e.key === 'ArrowLeft') {
            // Previous section
            const prevLink = document.querySelector('.content-section.active .nav-prev');
            if (prevLink) prevLink.click();
        } else if (e.key === 'ArrowRight') {
            // Next section
            const nextLink = document.querySelector('.content-section.active .nav-next');
            if (nextLink) nextLink.click();
        }
    }
});

// ============================================
// Print Support
// ============================================

function printCurrentSection() {
    const activeSection = document.querySelector('.content-section.active');
    if (activeSection) {
        const printWindow = window.open('', '_blank');
        printWindow.document.write(`
            <!DOCTYPE html>
            <html>
            <head>
                <title>Print Section</title>
                <link rel="stylesheet" href="styles.css">
                <link rel="stylesheet" href="contents-reader.css">
            </head>
            <body>
                ${activeSection.innerHTML}
            </body>
            </html>
        `);
        printWindow.document.close();
        printWindow.print();
    }
}

// ============================================
// Export Utilities
// ============================================

// Export functions for external use if needed
window.bookReader = {
    navigateToSection,
    printCurrentSection
};
