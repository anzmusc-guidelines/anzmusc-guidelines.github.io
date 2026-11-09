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

// Remembers which element opened the modal, so focus can return there on close.
let lastFocusedTrigger = null;

const FOCUSABLE_SELECTOR = 'a[href], button:not([disabled]), input:not([disabled]), textarea:not([disabled]), select:not([disabled]), [tabindex]:not([tabindex="-1"])';

// Return the modal's real (non-sentinel) focusable elements that are visible.
function getModalFocusables(modal) {
    return [...modal.querySelectorAll(FOCUSABLE_SELECTOR)]
        .filter(el => !el.classList.contains('focus-sentinel'))
        .filter(el => el.offsetWidth > 0 || el.offsetHeight > 0 || el === document.activeElement);
}

// Add two invisible focusable "sentinels" just inside the modal content — one at the
// very start, one at the very end. Because they are <div tabindex="0"> (not links),
// every browser including Safari puts them in the tab order. When the user tabs onto
// a sentinel, we know they've reached a boundary and bounce focus to the other end.
// This is browser-agnostic and doesn't depend on which elements Safari will focus.
function ensureSentinels(modal) {
    const content = modal.querySelector('.modal-content') || modal;
    if (content.querySelector(':scope > .focus-sentinel')) return; // already added

    const makeSentinel = (pos) => {
        const s = document.createElement('div');
        s.className = 'focus-sentinel';
        s.tabIndex = 0;
        s.setAttribute('aria-hidden', 'true');
        s.dataset.sentinel = pos;
        // Visually hidden but focusable.
        s.style.cssText = 'position:absolute;width:1px;height:1px;padding:0;margin:-1px;overflow:hidden;clip:rect(0,0,0,0);border:0;';
        return s;
    };
    content.insertBefore(makeSentinel('start'), content.firstChild);
    content.appendChild(makeSentinel('end'));
}

function openModal(modalId) {
    // Close any existing modals first
    document.querySelectorAll('.modal-overlay').forEach(modal => modal.classList.remove('active'));

    const modal = document.getElementById('modal-' + modalId);
    if (modal) {
        // Was this modal already open? (Re-opening the same rec, e.g. via a hash
        // change to one of its tabs, should not count as a second view.)
        const wasActive = modal.classList.contains('active');
        lastFocusedTrigger = document.activeElement;

        modal.classList.add('active');
        document.body.style.overflow = 'hidden';

        // Dialog semantics for screen readers.
        modal.setAttribute('role', 'dialog');
        modal.setAttribute('aria-modal', 'true');
        const titleEl = modal.querySelector('.modal-title');
        if (titleEl) {
            if (!titleEl.id) titleEl.id = modalId + '-title';
            modal.setAttribute('aria-labelledby', titleEl.id);
        }

        ensureSentinels(modal);

        const modalBody = modal.querySelector('.modal-body');
        if (modalBody) modalBody.scrollTop = 0;

        activateTab(modalId, 'recommendation');

        // Move focus to the close button (a safe, always-present first stop).
        const closeBtn = modal.querySelector('.modal-close');
        if (closeBtn) closeBtn.focus();

        if (!wasActive) trackRecommendation('view_recommendation', modalId);
    }
}

function closeModal() {
    document.querySelectorAll('.modal-overlay').forEach(modal => modal.classList.remove('active'));
    document.body.style.overflow = '';

    if (lastFocusedTrigger && typeof lastFocusedTrigger.focus === 'function') {
        lastFocusedTrigger.focus();
    }
    lastFocusedTrigger = null;
}

// Show one tab of a modal. Returns true if the tab actually changed.
function activateTab(modalId, tabId) {
    const modal = document.getElementById('modal-' + modalId);
    if (!modal) return false;
    const current = modal.querySelector('.modal-tab.active');
    const changed = !current || current.dataset.tab !== tabId;
    modal.querySelectorAll('.modal-tab').forEach(tab => tab.classList.toggle('active', tab.dataset.tab === tabId));
    modal.querySelectorAll('.tab-content').forEach(content => content.classList.remove('active'));
    const tabContent = document.getElementById(modalId + '-' + tabId);
    if (tabContent) tabContent.classList.add('active');
    return changed;
}

// Called from the tab buttons (onclick="switchTab('rec-0', 'etd')") and by
// deep links with a /tab suffix. Records which tab of which rec was read.
function switchTab(modalId, tabId) {
    if (activateTab(modalId, tabId)) trackRecommendation('view_recommendation_tab', modalId, tabId);
}

// ============================================================
// Google Analytics: per-recommendation events
// GA4 only records page views by default, and opening a recommendation
// doesn't change the page, so the Analytics reports can't otherwise tell
// WHICH recommendation was read. These two custom events fill that gap:
//   view_recommendation      - a rec's modal was opened (click, deep link or site search)
//   view_recommendation_tab  - a tab other than the one shown on opening was chosen
// Each carries recommendation_id (rec-18), recommendation_slug (hcq-retinopathy),
// recommendation_title (card title), guideline (adult/jia) and, for tabs, tab.
// To see the parameters in GA4 reports or the Data API they must be registered
// once as event-scoped custom dimensions (Admin -> Custom definitions) -
// see .claude/skills/analytics-report. Does nothing if gtag isn't loaded.
// ============================================================
function trackRecommendation(eventName, modalId, tabId) {
    if (typeof window.gtag !== 'function') return;
    const modal = document.getElementById('modal-' + modalId);
    const title = modal?.querySelector('.modal-title')?.textContent.replace(/\s+/g, ' ').trim() || '';
    const slugMap = window.adultSlugMap || window.jiaSlugMap || {};
    const slug = Object.keys(slugMap).find(k => slugMap[k] === modalId) || '';
    const params = {
        recommendation_id: modalId,
        recommendation_slug: slug,
        recommendation_title: title.slice(0, 100), // GA4 caps parameter values at 100 chars
        guideline: window.adultSlugMap ? 'adult' : (window.jiaSlugMap ? 'jia' : '')
    };
    if (tabId) params.tab = tabId;
    window.gtag('event', eventName, params);
}

document.querySelectorAll('.modal-overlay').forEach(modal => {
    modal.addEventListener('click', function(e) { if (e.target === this) closeModal(); });
});

document.addEventListener('keydown', function(e) { if (e.key === 'Escape') closeModal(); });

// Focus trap via sentinels: when focus lands on a boundary sentinel, bounce it to
// the opposite end of the modal's real content. Works identically in all browsers.
document.addEventListener('focusin', function(e) {
    const target = e.target;
    if (!target.classList || !target.classList.contains('focus-sentinel')) return;

    const modal = target.closest('.modal-overlay.active');
    if (!modal) return;

    const focusables = getModalFocusables(modal);
    if (focusables.length === 0) return;

    if (target.dataset.sentinel === 'start') {
        // Tabbed backwards past the top -> go to the last real element.
        focusables[focusables.length - 1].focus();
    } else {
        // Tabbed forwards past the bottom -> go to the first real element.
        focusables[0].focus();
    }
});

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

    let hashValue = hash.substring(1); // Remove the #
    // Optional "/tab" suffix (e.g. #csdmard-reduction-ra/practical) opens that tab - used by site search
    let tabId = null;
    const slash = hashValue.indexOf('/');
    if (slash > 0) { tabId = hashValue.substring(slash + 1); hashValue = hashValue.substring(0, slash); }
    const openWithTab = (id) => { openModal(id); if (tabId) switchTab(id, tabId); };

    // Numeric formats. Check jia-rec- before rec- because "jia-rec-1" also
    // technically starts after the prefix test; explicit ordering keeps it clear.
    if (hashValue.startsWith('jia-rec-') || hashValue.startsWith('rec-')) {
        openWithTab(hashValue);
        return;
    }

    // Slug maps: use whichever the page provides.
    const slugMap = window.adultSlugMap || window.jiaSlugMap;
    if (slugMap && slugMap[hashValue]) {
        openWithTab(slugMap[hashValue]);
        return;
    }
}

// Check on page load
document.addEventListener('DOMContentLoaded', checkHashAndOpenModal);
window.checkHashAndOpenModal = checkHashAndOpenModal;

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
