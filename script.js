// ============================================
// Spatial Intelligence Survey - JavaScript
// ============================================

// Smooth scroll for anchor links
document.addEventListener('DOMContentLoaded', function() {
    // Mobile navigation toggle
    const navToggle = document.querySelector('.nav-toggle');
    const navMenu = document.querySelector('.nav-menu');

    if (navToggle && navMenu) {
        navToggle.addEventListener('click', function() {
            navMenu.classList.toggle('active');

            // Animate hamburger icon
            const spans = navToggle.querySelectorAll('span');
            if (navMenu.classList.contains('active')) {
                spans[0].style.transform = 'rotate(45deg) translate(6px, 6px)';
                spans[1].style.opacity = '0';
                spans[2].style.transform = 'rotate(-45deg) translate(6px, -6px)';
            } else {
                spans[0].style.transform = 'none';
                spans[1].style.opacity = '1';
                spans[2].style.transform = 'none';
            }
        });

        // Close menu when clicking a link
        document.querySelectorAll('.nav-link').forEach(link => {
            link.addEventListener('click', function() {
                navMenu.classList.remove('active');
                const spans = navToggle.querySelectorAll('span');
                spans[0].style.transform = 'none';
                spans[1].style.opacity = '1';
                spans[2].style.transform = 'none';
            });
        });
    }

    // Smooth scrolling for internal links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });

    // Add copy functionality to citation code block
    const codeBlock = document.querySelector('pre code');
    if (codeBlock) {
        const copyButton = document.createElement('button');
        copyButton.textContent = '📋 Copy';
        copyButton.style.cssText = `
            position: absolute;
            top: 1rem;
            right: 1rem;
            padding: 0.5rem 1rem;
            background: var(--accent);
            color: white;
            border: none;
            border-radius: 6px;
            cursor: pointer;
            font-size: 0.875rem;
            font-weight: 600;
            transition: all 0.3s ease;
        `;

        const preElement = codeBlock.parentElement;
        preElement.style.position = 'relative';
        preElement.appendChild(copyButton);

        copyButton.addEventListener('click', async function() {
            try {
                await navigator.clipboard.writeText(codeBlock.textContent);
                copyButton.textContent = '✓ Copied!';
                setTimeout(() => {
                    copyButton.textContent = '📋 Copy';
                }, 2000);
            } catch (err) {
                console.error('Failed to copy:', err);
            }
        });

        copyButton.addEventListener('mouseenter', function() {
            this.style.transform = 'scale(1.05)';
        });

        copyButton.addEventListener('mouseleave', function() {
            this.style.transform = 'scale(1)';
        });
    }

    // Optional: Add scroll progress indicator
    createScrollProgress();
});

// Scroll Progress Indicator
function createScrollProgress() {
    const progressBar = document.createElement('div');
    progressBar.style.cssText = `
        position: fixed;
        top: 0;
        left: 0;
        width: 0%;
        height: 4px;
        background: linear-gradient(90deg, var(--accent), var(--accent-hover));
        z-index: 9999;
        transition: width 0.1s ease;
    `;
    document.body.appendChild(progressBar);

    window.addEventListener('scroll', function() {
        const windowHeight = document.documentElement.scrollHeight - document.documentElement.clientHeight;
        const scrolled = (window.scrollY / windowHeight) * 100;
        progressBar.style.width = scrolled + '%';
    });
}

// ============================================
// Literature Search Page Functions
// ============================================

function performSearch() {
    const searchTerm = document.getElementById('searchInput')?.value.toLowerCase();
    console.log('Searching for:', searchTerm);
    // TODO: Implement actual search functionality
    // This would typically query a backend API or search through a local database
    updateResultsCount();
}

function applyFilters() {
    const yearFilter = document.getElementById('yearFilter')?.value;
    const topicFilter = document.getElementById('topicFilter')?.value;
    const venueFilter = document.getElementById('venueFilter')?.value;

    console.log('Applying filters:', { yearFilter, topicFilter, venueFilter });
    // TODO: Implement actual filtering logic
    updateResultsCount();
}

function sortResults() {
    const sortBy = document.getElementById('sortBy')?.value;
    console.log('Sorting by:', sortBy);
    // TODO: Implement actual sorting logic
}

function updateResultsCount() {
    const countElement = document.getElementById('resultsCount');
    if (countElement) {
        // TODO: Update with actual count after filtering
        countElement.textContent = 'Showing 2,500+ references';
    }
}

function copyBibtex(button) {
    // TODO: Implement actual BibTeX copying
    // For now, just show feedback
    const originalText = button.textContent;
    button.textContent = 'Copied!';
    button.style.background = '#4CAF50';
    button.style.color = 'white';

    setTimeout(() => {
        button.textContent = originalText;
        button.style.background = '';
        button.style.color = '';
    }, 2000);
}

function loadMore() {
    console.log('Loading more results...');
    // TODO: Implement pagination
}

// ============================================
// Errata Submission Page Functions
// ============================================

function submitErrata(event) {
    event.preventDefault();

    const formData = {
        reporterName: document.getElementById('reporterName')?.value,
        reporterEmail: document.getElementById('reporterEmail')?.value,
        issueType: document.getElementById('issueType')?.value,
        chapter: document.getElementById('chapter')?.value,
        pageNumber: document.getElementById('pageNumber')?.value,
        description: document.getElementById('description')?.value,
        suggestion: document.getElementById('suggestion')?.value
    };

    console.log('Submitting errata:', formData);

    // TODO: Implement actual form submission to backend
    // For now, show success message
    const form = document.getElementById('errataForm');
    const successMessage = document.getElementById('successMessage');

    if (form && successMessage) {
        form.style.display = 'none';
        successMessage.style.display = 'block';

        // Scroll to success message
        successMessage.scrollIntoView({ behavior: 'smooth', block: 'center' });

        // Reset form after delay
        setTimeout(() => {
            form.reset();
            form.style.display = 'block';
            successMessage.style.display = 'none';
        }, 5000);
    }

    return false;
}

