// NCDR CathPCI Coding Guidelines Application
let allGuidelines = [];
let currentFilter = 'all';
let searchQuery = '';
let seqQuery = '';

// Initialize the application
document.addEventListener('DOMContentLoaded', function() {
    loadGuidelines();
    initializeEventListeners();
});

// Load guidelines data from JSON
async function loadGuidelines() {
    try {
        const response = await fetch('ncdr_guidelines_data.json');
        allGuidelines = await response.json();
        
        document.getElementById('loading').style.display = 'none';
        document.getElementById('guidelinesGrid').style.display = 'grid';

        renderGuidelines();
    } catch (error) {
        console.error('Error loading guidelines:', error);
        document.getElementById('loading').innerHTML = '<p style="color: var(--error);">Error loading guidelines data. Please refresh the page.</p>';
    }
}

// Event listeners
function initializeEventListeners() {
    // Keyword search
    const searchInput = document.getElementById('searchInput');
    searchInput.addEventListener('input', function(e) {
        searchQuery = e.target.value.toLowerCase();
        renderGuidelines();
    });

    // Sequence number search
    const seqInput = document.getElementById('seqInput');
    seqInput.addEventListener('input', function(e) {
        seqQuery = e.target.value.trim();
        renderGuidelines();
    });

    // Source filter buttons
    const filterButtons = document.querySelectorAll('.filter-btn');
    filterButtons.forEach(button => {
        button.addEventListener('click', function() {
            filterButtons.forEach(btn => btn.classList.remove('active'));
            this.classList.add('active');
            currentFilter = this.dataset.source;
            renderGuidelines();
        });
    });
}

// Filter guidelines based on current filters and search
function filterGuidelines() {
    return allGuidelines.filter(guideline => {
        // Source filter
        const sourceMatch = currentFilter === 'all' || guideline.source === currentFilter;
        
        // Sequence number search
        const seqMatch = !seqQuery || (guideline.sequence && guideline.sequence.includes(seqQuery));
        
        // Keyword search - search across all text fields
        let keywordMatch = true;
        if (searchQuery) {
            const searchableText = [
                guideline.sequence || '',
                guideline.element_name || '',
                guideline.data_field || '',
                guideline.question || '',
                guideline.answer || '',
                guideline.rationale || '',
                guideline.definition || '',
                guideline.content || '',
                guideline.section || '',
                ...(guideline.keywords || [])
            ].join(' ').toLowerCase();
            
            keywordMatch = searchableText.includes(searchQuery);
        }
        
        return sourceMatch && seqMatch && keywordMatch;
    });
}

// Render guidelines to the grid
function renderGuidelines() {
    const grid = document.getElementById('guidelinesGrid');
    const noResults = document.getElementById('noResults');
    const filteredGuidelines = filterGuidelines();
    
    // Clear existing content
    grid.innerHTML = '';
    
    if (filteredGuidelines.length === 0) {
        grid.style.display = 'none';
        noResults.style.display = 'block';
    } else {
        grid.style.display = 'grid';
        noResults.style.display = 'none';
        
        filteredGuidelines.forEach((guideline, index) => {
            const card = createGuidelineCard(guideline, index);
            grid.appendChild(card);
        });
    }
}

// Create a guideline card element
function createGuidelineCard(guideline, index) {
    const card = document.createElement('div');
    card.className = 'guideline-card';
    card.style.animationDelay = `${Math.min(index * 0.05, 1)}s`;
    
    // Determine card title and content based on source
    let titleHTML = '';
    let contentHTML = '';
    
    if (guideline.source === 'Additional Coding Directives (FAQs)') {
        titleHTML = guideline.element_name || 'Coding Directive';
        
        if (guideline.question) {
            contentHTML += `<div class="content-section">
                <h4>Question</h4>
                <p>${escapeHtml(guideline.question)}</p>
            </div>`;
        }
        
        if (guideline.answer) {
            contentHTML += `<div class="content-section">
                <h4>Answer</h4>
                <p>${escapeHtml(guideline.answer)}</p>
            </div>`;
        }
        
        if (guideline.definition) {
            contentHTML += `<div class="content-section">
                <h4>Definition</h4>
                <p>${escapeHtml(guideline.definition)}</p>
            </div>`;
        }
    } else if (guideline.source === 'Questions from your Peers') {
        titleHTML = guideline.data_field || 'Peer Question';
        
        if (guideline.question) {
            contentHTML += `<div class="content-section">
                <h4>Question</h4>
                <p>${escapeHtml(guideline.question)}</p>
            </div>`;
        }
        
        if (guideline.answer) {
            contentHTML += `<div class="content-section">
                <h4>Answer</h4>
                <p><strong>${escapeHtml(guideline.answer)}</strong></p>
            </div>`;
        }
        
        if (guideline.rationale) {
            contentHTML += `<div class="content-section">
                <h4>Rationale</h4>
                <p>${escapeHtml(guideline.rationale)}</p>
            </div>`;
        }
    } else if (guideline.source === 'Supplemental Dictionary') {
        titleHTML = guideline.section || 'Supplemental Entry';
        contentHTML = `<div class="guideline-content">${escapeHtml(guideline.content || '')}</div>`;
    } else {
        // Data Dictionary or other
        titleHTML = 'Data Dictionary Entry';
        contentHTML = `<div class="guideline-content">${escapeHtml(guideline.content || '')}</div>`;
    }
    
    // Build sequence badge if available
    let seqBadge = '';
    if (guideline.sequence) {
        seqBadge = `<span class="sequence-badge">Seq #${guideline.sequence}</span>`;
    }
    
    card.innerHTML = `
        <div class="guideline-header">
            <div class="guideline-title">${escapeHtml(titleHTML)}</div>
            <div class="guideline-meta">
                ${seqBadge}
                <div class="guideline-id">${guideline.id}</div>
            </div>
        </div>
        <div class="tags">
            <span class="tag source">${guideline.source}</span>
            <span class="tag date">📅 ${guideline.published_date}</span>
        </div>
        ${contentHTML}
    `;
    
    return card;
}

// Escape HTML to prevent XSS
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// Helper function to clear all filters
function clearFilters() {
    document.getElementById('searchInput').value = '';
    document.getElementById('seqInput').value = '';
    searchQuery = '';
    seqQuery = '';
    currentFilter = 'all';
    
    const filterButtons = document.querySelectorAll('.filter-btn');
    filterButtons.forEach(btn => btn.classList.remove('active'));
    document.querySelector('[data-source="all"]').classList.add('active');
    
    renderGuidelines();
}
