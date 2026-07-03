// Australian Living Guidelines - Shared Scripts
// Works on BOTH the Adult IA page and the JIA page.
// Supports numeric (#rec-0 / #jia-rec-1) and slug-based (#initial-dmard-ra) URLs.
//
// Design note: the Adult page has condition tabs (RA/PsA/AxSpA/SLE); the JIA
// page does not. This script is written so that every page-specific feature is
// optional — if the element isn't on the page, that feature quietly does nothing.

let activeCondition = 'all';
let activeTag = null;
let searchQuery = '';

function filterCards() {
    let visibleCount = 0;
    document.querySelectorAll('.recommendation-card').forEach(card => {
        const conditions = card.dataset.conditions || '';
        const tags = card.dataset.tags || '';
        const title = card.querySelector('.card-title')?.textContent.toLowerCase() || '';
        const recommendation = card.querySelector('.card-recommendation')?.textContent.toLowerCase() || '';
        const category = card.querySelector('.card-category')?.textContent.toLowerCase() || '';

        const onclickAttr = card.getAttribute('onclick') || '';
        const modalIdMatch = onclickAttr.match(/openModal\('([^']+)'\)/);
        let modalContent = '';

        if (modalIdMatch && searchQuery) {
            const modalId = modalIdMatch[1];
            const modal = document.getElementById('modal-' + modalId);
            if (modal) {
                modalContent = modal.textContent.toLowerCase();
            }
        }

        const matchesCondition = activeCondition === 'all' || conditions.includes(activeCondition);
        const matchesTag = !activeTag || tags.includes(activeTag);
        const matchesSearch = !searchQuery ||
            title.includes(searchQuery) ||
            recommendation.includes(searchQuery) ||
            category.includes(searchQuery) ||
            tags.includes(searchQuery) ||
            modalContent.includes(searchQuery);

        const isVisible = matchesCondition && matchesTag && matchesSearch;
        card.classList.toggle('hidden', !isVisible);
        if (isVisible) visibleCount++;
    });

    // "No results" message: use an existing element if the page provides one
    // (the JIA page does), otherwise create one after the grid (the Adult page).
    let noResults = document.getElementById('no-results');
    if (visibleCount === 0) {
        if (!noResults) {
            const grid = document.getElementById('recommendations-grid');
            if (grid) {
                noResults = document.createElement('div');
                noResults.id = 'no-results';
                noResults.className = 'no-results';
                noResults.innerHTML = '<h3>No recommendations found</h3><p>Try adjusting your search or filters</p>';
                grid.after(noResults);
            }
        }
        if (noResults) noResults.style.display = 'block';
    } else if (noResults) {
        noResults.style.display = 'none';
    }
}

const searchInput = document.getElementById('search-input');
const searchClear = document.getElementById('search-clear');

if (searchInput) {
    searchInput.addEventListener('input', function() {
        searchQuery = this.value.toLowerCase().trim();
        if (searchClear) searchClear.classList.toggle('visible', searchQuery.length > 0);
        filterCards();
    });
}

function clearSearch() {
    if (searchInput) searchInput.value = '';
    searchQuery = '';
    if (searchClear) searchClear.classList.remove('visible');
    filterCards();
}

// Condition tabs are Adult-only; on the JIA page this selector finds nothing
// and the block is simply skipped.
document.querySelectorAll('.condition-tab').forEach(tab => {
    tab.addEventListener('click', function() {
        document.querySelectorAll('.condition-tab').forEach(t => t.classList.remove('active'));
        this.classList.add('active');
        activeCondition = this.dataset.condition;
        filterCards();
    });
});

document.querySelectorAll('.tag-filter').forEach(btn => {
    btn.addEventListener('click', function() {
        if (this.classList.contains('active')) {
            this.classList.remove('active');
            activeTag = null;
        } else {
            document.querySelectorAll('.tag-filter').forEach(b => b.classList.remove('active'));
            this.classList.add('active');
            activeTag = this.dataset.tag;
        }
        filterCards();
    });
});

function openModal(modalId) {
    // Close any existing modals first
    document.querySelectorAll('.modal-overlay').forEach(modal => modal.classList.remove('active'));

    const modal = document.getElementById('modal-' + modalId);
    if (modal) {
        modal.classList.add('active');
        document.body.style.overflow = 'hidden';

        // Scroll modal body to top
        const modalBody = modal.querySelector('.modal-body');
        if (modalBody) {
            modalBody.scrollTop = 0;
        }

        // Reset to Recommendation tab
        switchTab(modalId, 'recommendation');
    }
}

function closeModal() {
    document.querySelectorAll('.modal-overlay').forEach(modal => modal.classList.remove('active'));
    document.body.style.overflow = '';
}

function switchTab(modalId, tabId) {
    const modal = document.getElementById('modal-' + modalId);
    if (!modal) return;
    modal.querySelectorAll('.modal-tab').forEach(tab => tab.classList.toggle('active', tab.dataset.tab === tabId));
    modal.querySelectorAll('.tab-content').forEach(content => content.classList.remove('active'));
    const tabContent = document.getElementById(modalId + '-' + tabId);
    if (tabContent) tabContent.classList.add('active');
}

document.querySelectorAll('.modal-overlay').forEach(modal => {
    modal.addEventListener('click', function(e) { if (e.target === this) closeModal(); });
});

document.addEventListener('keydown', function(e) { if (e.key === 'Escape') closeModal(); });

// Smooth-scroll for in-page anchor links. Links that open a modal carry their
// own onclick="...; return false;" so they never reach this handler; this only
// affects plain jump links such as "Browse Recommendations" (#recommendations).
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function(e) {
        const href = this.getAttribute('href');
        if (href === '#') return; // ignore placeholder nav links
        const target = document.querySelector(href);
        if (target) {
            e.preventDefault();
            target.scrollIntoView({ behavior: 'smooth', block: 'start' });
        }
    });
});

// Deep linking - open modal from URL hash.
// Supports numeric (#rec-0, #jia-rec-1) and slug-based URLs, using whichever
// slug map the current page defines (adultSlugMap or jiaSlugMap).
function checkHashAndOpenModal() {
    const hash = window.location.hash;
    if (!hash || hash.length <= 1) return;

    const hashValue = hash.substring(1); // Remove the #

    // Numeric formats. Check jia-rec- before rec- because "jia-rec-1" also
    // technically starts after the prefix test; explicit ordering keeps it clear.
    if (hashValue.startsWith('jia-rec-') || hashValue.startsWith('rec-')) {
        openModal(hashValue);
        return;
    }

    // Slug maps: use whichever the page provides.
    const slugMap = window.adultSlugMap || window.jiaSlugMap;
    if (slugMap && slugMap[hashValue]) {
        openModal(slugMap[hashValue]);
        return;
    }
}

// Check on page load
document.addEventListener('DOMContentLoaded', checkHashAndOpenModal);

// Also check if hash changes while on page
window.addEventListener('hashchange', checkHashAndOpenModal);

// ============================================================
// Keyboard accessibility for click-to-open elements (Step 3b)
// Cards and What's New items open a modal on mouse click via their
// onclick attribute. This block makes them equally operable by keyboard
// and understandable to screen readers, WITHOUT any change to the HTML —
// so every future recommendation inherits this automatically.
// ============================================================
(function enableKeyboardForModalOpeners() {
    // Elements that open a modal on click but aren't natively focusable.
    const openers = document.querySelectorAll('.recommendation-card, .whats-new-item');

    openers.forEach(el => {
        // Skip if it doesn't actually open a modal.
        const onclick = el.getAttribute('onclick') || '';
        if (!onclick.includes('openModal')) return;

        // 1. Make it reachable by Tab.
        if (!el.hasAttribute('tabindex')) el.setAttribute('tabindex', '0');

        // 2. Announce it as an interactive control that opens a dialog.
        if (!el.hasAttribute('role')) el.setAttribute('role', 'button');
        el.setAttribute('aria-haspopup', 'dialog');

        // 3. Give screen readers a meaningful name, derived from the card's
        //    own title so it can never drift out of sync with the content.
        if (!el.hasAttribute('aria-label')) {
            const titleEl = el.querySelector('.card-title, .whats-new-title');
            const title = titleEl ? titleEl.textContent.trim() : 'recommendation';
            el.setAttribute('aria-label', title + ' — open details');
        }

        // 4. Activate on Enter or Space, the standard keys for a button.
        //    Space is prevented from also scrolling the page.
        el.addEventListener('keydown', function(e) {
            if (e.key === 'Enter' || e.key === ' ' || e.key === 'Spacebar') {
                e.preventDefault();
                el.click();
            }
        });
    });
})();
