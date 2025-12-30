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
    
    let noResults = document.getElementById('no-results');
    if (visibleCount === 0) {
        if (!noResults) {
            noResults = document.createElement('div');
            noResults.id = 'no-results';
            noResults.className = 'no-results';
            noResults.innerHTML = '<h3>No recommendations found</h3><p>Try adjusting your search or filters</p>';
            document.getElementById('recommendations-grid').after(noResults);
        }
        noResults.style.display = 'block';
    } else if (noResults) {
        noResults.style.display = 'none';
    }
}

const searchInput = document.getElementById('search-input');
const searchClear = document.getElementById('search-clear');

searchInput.addEventListener('input', function() {
    searchQuery = this.value.toLowerCase().trim();
    searchClear.classList.toggle('visible', searchQuery.length > 0);
    filterCards();
});

function clearSearch() {
    searchInput.value = '';
    searchQuery = '';
    searchClear.classList.remove('visible');
    filterCards();
}

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
    const modal = document.getElementById('modal-' + modalId);
    if (modal) { 
        modal.classList.add('active'); 
        document.body.style.overflow = 'hidden'; 
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

document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function(e) {
        e.preventDefault();
        const target = document.querySelector(this.getAttribute('href'));
        if (target) target.scrollIntoView({ behavior: 'smooth', block: 'start' });
    });
});
