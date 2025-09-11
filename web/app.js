// URLXpanda Web Application
class URLXpandaApp {
    constructor() {
        this.history = this.loadHistory();
        this.isProcessing = false;
        
        this.initializeElements();
        this.attachEventListeners();
        this.renderHistory();
    }

    initializeElements() {
        // Input elements
        this.urlInput = document.getElementById('url-input');
        this.expandBtn = document.getElementById('expand-btn');

        // Result elements
        this.resultContainer = document.getElementById('result-container');
        this.errorContainer = document.getElementById('error-container');
        this.originalUrl = document.getElementById('original-url');
        this.finalUrl = document.getElementById('final-url');
        this.redirectCount = document.getElementById('redirect-count');
        this.expansionTime = document.getElementById('expansion-time');
        this.errorMessage = document.getElementById('error-message');

        // Action buttons
        this.copyBtn = document.getElementById('copy-btn');
        this.retryBtn = document.getElementById('retry-btn');
        this.clearHistoryBtn = document.getElementById('clear-history');

        // History elements
        this.historyList = document.getElementById('history-list');

        // Modal elements
        this.aboutModal = document.getElementById('about-modal');
        this.aboutLink = document.getElementById('about-link');
        this.closeModalBtn = document.getElementById('close-modal');
    }

    attachEventListeners() {
        // Main functionality
        this.expandBtn.addEventListener('click', () => this.expandUrl());
        this.urlInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') this.expandUrl();
        });
        this.urlInput.addEventListener('input', () => this.validateInput());

        // Actions
        this.copyBtn.addEventListener('click', () => this.copyToClipboard());
        this.retryBtn.addEventListener('click', () => this.expandUrl());
        this.clearHistoryBtn.addEventListener('click', () => this.clearHistory());

        // Modal
        this.aboutLink.addEventListener('click', (e) => {
            e.preventDefault();
            this.showModal();
        });
        this.closeModalBtn.addEventListener('click', () => this.hideModal());
        this.aboutModal.addEventListener('click', (e) => {
            if (e.target === this.aboutModal) this.hideModal();
        });

        // Keyboard shortcuts
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') this.hideModal();
            if (e.ctrlKey && e.key === 'Enter') this.expandUrl();
        });
    }

    validateInput() {
        const url = this.urlInput.value.trim();
        const isValid = this.isValidUrl(url);
        
        this.expandBtn.disabled = !isValid || this.isProcessing;
        
        if (url && !isValid) {
            this.urlInput.setCustomValidity('Please enter a valid URL');
        } else {
            this.urlInput.setCustomValidity('');
        }
    }

    isValidUrl(string) {
        try {
            const url = new URL(string);
            return url.protocol === 'http:' || url.protocol === 'https:';
        } catch {
            return false;
        }
    }

    async expandUrl() {
        if (this.isProcessing) return;
        
        const url = this.urlInput.value.trim();
        if (!this.isValidUrl(url)) {
            this.showNotification('Please enter a valid URL', 'error');
            return;
        }

        this.setLoadingState(true);
        this.hideResults();
        
        try {
            console.log('Expanding URL:', url);
            
            const response = await fetch(`/api/expand?url=${encodeURIComponent(url)}`);
            const result = await response.json();

            if (!response.ok) {
                throw new Error(result.error || 'Failed to expand URL');
            }

            console.log('Expansion result:', result);
            console.log('Has metadata:', !!result.metadata);
            
            if (result.metadata) {
                console.log('Showing rich result with metadata');
                this.showRichResult(result);
            } else {
                console.log('Showing simple result - no metadata');
                this.showSimpleResult(result);
            }
            this.addToHistory(result.original_url, result.final_url, result.expansion_time_ms);
            this.showNotification('URL processed successfully!', 'success');
            
        } catch (error) {
            console.error('URL expansion failed:', error);
            this.showError(error.toString());
            this.showNotification('Failed to expand URL', 'error');
        } finally {
            this.setLoadingState(false);
        }
    }
