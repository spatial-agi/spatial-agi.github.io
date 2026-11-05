// Static LaTeX book reader. All content is present in contents.html for file:// and hosting.
document.addEventListener('DOMContentLoaded', () => {
    const content = document.getElementById('contentArea');
    const sidebar = document.getElementById('sidebar');
    const menu = document.getElementById('readerMenuToggle');
    const sections = [...content.querySelectorAll('.content-section')];
    const tocLinks = [...sidebar.querySelectorAll('.toc-link')];
    const anchorMap = new Map();
    sections.forEach(section => {
        anchorMap.set(section.id, section);
        section.querySelectorAll('[id]').forEach(node => anchorMap.set(node.id, section));
    });
    let routeVersion = 0;
    let citationPopup = null;
    let citationTrigger = null;

    function setSidebar(open) {
        sidebar.classList.toggle('open', open);
        menu?.setAttribute('aria-expanded', String(open));
    }
    menu?.addEventListener('click', () => setSidebar(!sidebar.classList.contains('open')));
    document.getElementById('sidebarToggle')?.addEventListener('click', () => setSidebar(false));

    async function showAnchor(id) {
        const section = anchorMap.get(id) || sections[0];
        if (!section) return;
        const version = ++routeVersion;
        sections.forEach(item => item.classList.toggle('active', item === section));
        document.title = `${section.querySelector('h1')?.textContent || 'Book Contents'} - Spatial Intelligence Survey`;
        const selected = tocLinks.find(link => link.hash === `#${id}`)
            || tocLinks.find(link => link.hash === `#${section.id}`);
        tocLinks.forEach(link => link.classList.toggle('active', link === selected));
        if (selected) {
            let parent = selected.parentElement;
            while (parent && parent !== sidebar) {
                if (parent.tagName === 'DETAILS') parent.open = true;
                parent = parent.parentElement;
            }
        }
        const scrollToTarget = () => {
            if (version !== routeVersion) return;
            const target = document.getElementById(id) || section;
            target.scrollIntoView({ block: 'start' });
        };
        scrollToTarget();
        // Typeset only the visible chapter. Wait for the async MathJax startup on first visit.
        if (window.MathJax?.startup?.promise) {
            try {
                await window.MathJax.startup.promise;
                if (version !== routeVersion) return;
                await window.MathJax.typesetPromise([section]);
                scrollToTarget();
            } catch (error) {
                console.warn('Math rendering failed:', error);
            }
        }
    }

    function currentAnchor() {
        try { return decodeURIComponent(location.hash.slice(1)); }
        catch (_) { return ''; }
    }

    function closeCitation() {
        citationPopup?.remove();
        citationPopup = null;
        citationTrigger?.setAttribute('aria-expanded', 'false');
        citationTrigger = null;
    }

    function placeCitationPopup() {
        if (!citationPopup || !citationTrigger) return;
        const trigger = citationTrigger.getBoundingClientRect();
        const popup = citationPopup.getBoundingClientRect();
        const margin = 12;
        let left = Math.max(margin, Math.min(trigger.left, innerWidth - popup.width - margin));
        let top = trigger.bottom + 10;
        if (top + popup.height > innerHeight - margin && trigger.top - popup.height - 10 >= margin) {
            top = trigger.top - popup.height - 10;
            citationPopup.classList.add('above');
        } else {
            citationPopup.classList.remove('above');
        }
        citationPopup.style.left = `${left}px`;
        citationPopup.style.top = `${Math.max(margin, top)}px`;
        citationPopup.style.setProperty('--citation-arrow-left', `${Math.max(12, Math.min(popup.width - 22, trigger.left + trigger.width / 2 - left - 5))}px`);
    }

    function openCitation(trigger) {
        closeCitation();
        let items;
        try { items = JSON.parse(trigger.dataset.citation || '[]'); }
        catch (_) { return; }
        if (!items.length) return;
        citationTrigger = trigger;
        trigger.setAttribute('aria-expanded', 'true');
        citationPopup = document.createElement('div');
        citationPopup.className = 'citation-popover';
        citationPopup.setAttribute('role', 'dialog');
        citationPopup.setAttribute('aria-label', 'Citation details');
        const header = document.createElement('div');
        header.className = 'citation-popover-header';
        const heading = document.createElement('strong');
        heading.textContent = items.length === 1 ? 'Reference' : `${items.length} references`;
        const close = document.createElement('button');
        close.type = 'button';
        close.className = 'citation-popover-close';
        close.setAttribute('aria-label', 'Close citation details');
        close.textContent = '×';
        close.addEventListener('click', closeCitation);
        header.append(heading, close);
        citationPopup.append(header);
        items.forEach(item => {
            const entry = document.createElement('article');
            entry.className = 'citation-popover-entry';
            const title = document.createElement('strong');
            title.className = 'citation-popover-title';
            title.textContent = item.title || item.key;
            entry.append(title);
            const authors = document.createElement('p');
            authors.textContent = item.author || 'Unknown author';
            entry.append(authors);
            const meta = document.createElement('p');
            meta.className = 'citation-popover-meta';
            meta.textContent = [item.year, item.venue].filter(Boolean).join(' · ');
            if (meta.textContent) entry.append(meta);
            if (item.doi || item.url) {
                const external = document.createElement('a');
                external.href = item.doi ? `https://doi.org/${item.doi}` : item.url;
                external.target = '_blank';
                external.rel = 'noopener noreferrer';
                external.textContent = item.doi ? `doi:${item.doi}` : 'Open source';
                entry.append(external);
            }
            const full = document.createElement('a');
            full.href = `#ref-${encodeURIComponent(item.key)}`;
            full.className = 'citation-full-reference';
            full.textContent = 'View in references';
            entry.append(full);
            citationPopup.append(entry);
        });
        document.body.append(citationPopup);
        placeCitationPopup();
        close.focus({ preventScroll: true });
    }

    document.addEventListener('click', event => {
        const cite = event.target.closest('.citation-bubble');
        if (cite) {
            event.preventDefault();
            if (citationTrigger === cite) closeCitation();
            else openCitation(cite);
            return;
        }
        if (citationPopup && !citationPopup.contains(event.target)) closeCitation();
        const link = event.target.closest('a[href^="#"]');
        if (!link || event.ctrlKey || event.metaKey || event.shiftKey || event.altKey) return;
        const id = decodeURIComponent(link.getAttribute('href').slice(1));
        if (!anchorMap.has(id)) return;
        event.preventDefault();
        if (location.hash !== `#${encodeURI(id)}`) history.pushState(null, '', `#${encodeURI(id)}`);
        showAnchor(id);
        if (window.innerWidth <= 768) setSidebar(false);
    });
    window.addEventListener('popstate', () => showAnchor(currentAnchor()));
    window.addEventListener('hashchange', () => showAnchor(currentAnchor()));
    document.addEventListener('keydown', event => {
        if (event.key === 'Escape' && citationPopup) {
            closeCitation();
            return;
        }
        if (event.key === 'Escape') setSidebar(false);
        if (!event.altKey || !['ArrowLeft', 'ArrowRight'].includes(event.key)) return;
        const active = content.querySelector('.content-section.active');
        active?.querySelector(event.key === 'ArrowLeft' ? '.nav-prev' : '.nav-next')?.click();
        event.preventDefault();
    });
    window.addEventListener('resize', placeCitationPopup);
    document.getElementById('contentArea')?.addEventListener('scroll', placeCitationPopup, { passive: true });
    showAnchor(currentAnchor());
    document.getElementById('MathJax-script')?.addEventListener('load', () => showAnchor(currentAnchor()), { once: true });
});
