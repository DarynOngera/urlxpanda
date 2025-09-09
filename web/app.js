// URLXpanda Web Application
class URLXpandaApp {
    constructor() {
        this.wasm = null;
        this.urlExpander = null;
        this.history = this.loadHistory();
        this.isProcessing = false;
        
        this.initializeElements();
        this.attachEventListeners();
        this.renderHistory();
        this.loadWasm();
    }

    initializeElements() {
        // Input elements
        this.urlInput = document.getElementById('url-input');
        this.expandBtn = document.getElementById('expand-btn');
        this.maxRedirectsInput = document.getElementById('max-redirects');
        this.timeoutInput = document.getElementById('timeout');

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

        // Settings
        this.maxRedirectsInput.addEventListener('change', () => this.updateSettings());
        this.timeoutInput.addEventListener('change', () => this.updateSettings());

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

    async loadWasm() {
        try {
            console.log('Loading WASM module...');
            
            // Import the WASM module (adjust path as needed)
            this.wasm = await import('./pkg/urlxpanda_wasm.js');
            await this.wasm.default();
            
            // Initialize the URL expander
            this.urlExpander = new this.wasm.UrlExpander();
            this.updateSettings();
            
            console.log('WASM module loaded successfully');
            this.showNotification('URLXpanda ready!', 'success');
            
        } catch (error) {
            console.error('Failed to load WASM module:', error);
            this.showNotification('Failed to load WASM module. Some features may not work.', 'error');
        }
    }

    validateInput() {
        const url = this.urlInput.value.trim();
        const isValid = this.isValidUrl(url);
        
        this.expandBtn.disabled = !isValid || this.isProcessing || !this.urlExpander;
        
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

    updateSettings() {
        if (!this.urlExpander) return;
        
        const maxRedirects = parseInt(this.maxRedirectsInput.value);
        const timeout = parseInt(this.timeoutInput.value);
        
        this.urlExpander.set_max_redirects(maxRedirects);
        this.urlExpander.set_timeout_ms(timeout);
    }

    async expandUrl() {
        if (this.isProcessing || !this.urlExpander) return;
        
        const url = this.urlInput.value.trim();
        if (!this.isValidUrl(url)) {
            this.showNotification('Please enter a valid URL', 'error');
            return;
        }

        this.setLoadingState(true);
        this.hideResults();
        
        try {
            console.log('Expanding URL:', url);
            
            const result = await this.urlExpander.expand_url(url);
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

    setLoadingState(loading) {
        this.isProcessing = loading;
        this.expandBtn.disabled = loading;
        this.expandBtn.classList.toggle('loading', loading);
        this.urlInput.disabled = loading;
    }

    showSimpleResult(result) {
        // Update basic info
        this.originalUrl.textContent = result.original_url;
        this.finalUrl.textContent = result.final_url;
        this.redirectCount.textContent = `${result.redirect_chain.length - 1} redirect${result.redirect_chain.length - 1 !== 1 ? 's' : ''}`;
        this.expansionTime.textContent = `${result.expansion_time_ms}ms`;
        
        // Clear rich content since we're not using it anymore
        const resultContent = this.resultContainer.querySelector('.result-content');
        if (resultContent) {
            resultContent.innerHTML = '';
        }
        
        this.resultContainer.classList.remove('hidden');
        this.errorContainer.classList.add('hidden');
    }

    showRichResult(result) {
        // Update basic info
        this.originalUrl.textContent = result.original_url;
        this.finalUrl.textContent = result.final_url;
        this.redirectCount.textContent = `${result.redirect_chain.length - 1} redirect${result.redirect_chain.length - 1 !== 1 ? 's' : ''}`;
        this.expansionTime.textContent = `${result.expansion_time_ms}ms`;
        
        // Generate and display rich content
        const resultContent = this.resultContainer.querySelector('.result-content');
        if (resultContent) {
            resultContent.innerHTML = this.generateRichResultHTML(result);
            
            // Add click handlers for images
            this.addImageClickHandlers();
        }
        
        this.resultContainer.classList.remove('hidden');
        this.errorContainer.classList.add('hidden');
    }

    addImageClickHandlers() {
        const previewImages = this.resultContainer.querySelectorAll('.preview-image img');
        previewImages.forEach(img => {
            img.addEventListener('click', () => {
                this.showImageModal(img.src, img.alt);
            });
            img.style.cursor = 'pointer';
        });
    }

    showImageModal(src, alt) {
        const modal = document.createElement('div');
        modal.className = 'image-modal';
        modal.innerHTML = `
            <div class="modal-backdrop">
                <div class="modal-content">
                    <button class="modal-close">&times;</button>
                    <img src="${src}" alt="${alt}" class="modal-image">
                </div>
            </div>
        `;
        
        document.body.appendChild(modal);
        
        // Close handlers
        const closeBtn = modal.querySelector('.modal-close');
        const backdrop = modal.querySelector('.modal-backdrop');
        
        const closeModal = () => {
            document.body.removeChild(modal);
        };
        
        closeBtn.addEventListener('click', closeModal);
        backdrop.addEventListener('click', (e) => {
            if (e.target === backdrop) closeModal();
        });
        
        // ESC key handler
        const handleEsc = (e) => {
            if (e.key === 'Escape') {
                closeModal();
                document.removeEventListener('keydown', handleEsc);
            }
        };
        document.addEventListener('keydown', handleEsc);
    }

    generateRichResultHTML(result) {
        const metadata = result.metadata;
        const redirectChain = result.redirect_chain;
        const safetyWarnings = result.safety_warnings || [];
        
        return `
            ${this.generateRedirectChainHTML(redirectChain)}
            ${metadata ? this.generatePreviewCardHTML(metadata, result.final_url) : ''}
            ${this.generateSafetyIndicatorsHTML(metadata)}
            ${this.generateMetaInfoHTML(result)}
        `;
    }

    generateRedirectChainHTML(redirectChain) {
        if (redirectChain.length <= 1) return '';
        
        const chainItems = redirectChain.map((hop, index) => {
            const isLast = index === redirectChain.length - 1;
            const domain = this.extractDomain(hop.url);
            const statusBadge = hop.status_code ? `<span class="status-badge status-${Math.floor(hop.status_code / 100)}">${hop.status_code}</span>` : '';
            
            return `
                <div class="redirect-hop ${isLast ? 'final-hop' : ''}">
                    <div class="hop-info">
                        <span class="hop-domain">${domain}</span>
                        ${statusBadge}
                    </div>
                    ${!isLast ? '<div class="redirect-arrow">→</div>' : ''}
                </div>
            `;
        }).join('');
        
        return `
            <div class="redirect-chain-section">
                <h4>Redirect Chain</h4>
                <div class="redirect-chain">
                    ${chainItems}
                </div>
            </div>
        `;
    }

    generatePreviewCardHTML(metadata, finalUrl) {
        const title = metadata.title || 'No title available';
        const description = metadata.description || 'No description available';
        const image = metadata.image;
        const siteName = metadata.site_name;
        
        return `
            <div class="preview-card">
                <div class="preview-header">
                    <h4>Page Preview</h4>
                    <div class="preview-domain">
                        🌐
                        <span>${metadata.is_safe?.domain || 'Unknown domain'}</span>
                        ${metadata.is_safe?.is_https ? '<span class="https-badge">🔒 HTTPS</span>' : '<span class="http-badge">⚠️ HTTP</span>'}
                    </div>
                </div>
                <div class="preview-content">
                    ${image ? `<div class="preview-image"><img src="${image}" alt="Preview" loading="lazy"></div>` : ''}
                    <div class="preview-text">
                        <h5 class="preview-title">${this.escapeHtml(title)}</h5>
                        <p class="preview-description">${this.escapeHtml(description)}</p>
                        <a href="${finalUrl}" target="_blank" rel="noopener" class="preview-link">Visit Page →</a>
                    </div>
                </div>
            </div>
        `;
    }

    generateSafetyIndicatorsHTML(metadata) {
        if (!metadata || !metadata.is_safe) return '';
        
        const safety = metadata.is_safe;
        const warnings = [];
        
        if (!safety.is_https) {
            warnings.push('This URL uses HTTP instead of HTTPS');
        }
        
        if (safety.is_suspicious) {
            warnings.push('This domain is known for URL shortening and may hide the final destination');
        }
        
        if (warnings.length === 0) {
            return `
                <div class="safety-indicators safe">
                    <span class="safety-icon">✅</span>
                    <span>This URL appears to be safe</span>
                </div>
            `;
        }
        
        const warningItems = warnings.map(warning => `<li>${warning}</li>`).join('');
        
        return `
            <div class="safety-indicators warning">
                <div class="safety-header">
                    <span class="safety-icon">⚠️</span>
                    <span>Safety Warnings</span>
                </div>
                <ul class="warning-list">
                    ${warningItems}
                </ul>
            </div>
        `;
    }

    generateMetaInfoHTML(result) {
        return `
            <div class="result-meta">
                <span class="meta-item">
                    <strong>Redirects:</strong> ${result.redirect_chain.length - 1}
                </span>
                <span class="meta-item">
                    <strong>Time:</strong> ${result.expansion_time_ms}ms
                </span>
                <span class="meta-item">
                    <strong>Final Domain:</strong> ${this.extractDomain(result.final_url)}
                </span>
            </div>
        `;
    }

    extractDomain(url) {
        try {
            return new URL(url).hostname;
        } catch {
            return url;
        }
    }

    attachResultEventListeners() {
        // Add click handlers for preview images
        const previewImages = this.resultContainer.querySelectorAll('.preview-image img');
        previewImages.forEach(img => {
            img.addEventListener('click', () => {
                this.showImageModal(img.src);
            });
        });
        
        // Add click handlers for redirect chain items
        const redirectHops = this.resultContainer.querySelectorAll('.redirect-hop');
        redirectHops.forEach((hop, index) => {
            hop.addEventListener('click', () => {
                const url = hop.querySelector('.hop-info').dataset.url;
                if (url) {
                    this.showHopDetails(url, index);
                }
            });
        });
    }

    showImageModal(imageSrc) {
        // Create and show image modal
        const modal = document.createElement('div');
        modal.className = 'image-modal';
        modal.innerHTML = `
            <div class="image-modal-content">
                <button class="close-image-modal">&times;</button>
                <img src="${imageSrc}" alt="Preview Image">
            </div>
        `;
        
        document.body.appendChild(modal);
        modal.classList.remove('hidden');
        
        // Close handlers
        const closeBtn = modal.querySelector('.close-image-modal');
        closeBtn.addEventListener('click', () => {
            document.body.removeChild(modal);
        });
        
        modal.addEventListener('click', (e) => {
            if (e.target === modal) {
                document.body.removeChild(modal);
            }
        });
    }

    showError(message) {
        this.errorMessage.textContent = message;
        this.errorContainer.classList.remove('hidden');
        this.resultContainer.classList.add('hidden');
    }

    hideResults() {
        this.resultContainer.classList.add('hidden');
        this.errorContainer.classList.add('hidden');
    }

    async copyToClipboard() {
        const finalUrl = this.finalUrl.textContent;
        
        try {
            await navigator.clipboard.writeText(finalUrl);
            this.showNotification('URL copied to clipboard!', 'success');
            
            // Visual feedback
            const originalText = this.copyBtn.innerHTML;
            this.copyBtn.innerHTML = '✓ Copied';
            setTimeout(() => {
                this.copyBtn.innerHTML = originalText;
            }, 2000);
            
        } catch (error) {
            console.error('Failed to copy to clipboard:', error);
            this.showNotification('Failed to copy URL', 'error');
        }
    }

    // History management
    loadHistory() {
        try {
            const stored = localStorage.getItem('urlxpanda-history');
            return stored ? JSON.parse(stored) : [];
        } catch {
            return [];
        }
    }

    saveHistory() {
        try {
            localStorage.setItem('urlxpanda-history', JSON.stringify(this.history));
        } catch (error) {
            console.error('Failed to save history:', error);
        }
    }

    addToHistory(original, final, expansionTime) {
        const entry = {
            id: Date.now(),
            original,
            final,
            expansionTime,
            timestamp: new Date().toISOString()
        };
        
        // Remove duplicates and add to front
        this.history = this.history.filter(item => item.original !== original);
        this.history.unshift(entry);
        
        // Keep only last 50 entries
        this.history = this.history.slice(0, 50);
        
        this.saveHistory();
        this.renderHistory();
    }

    renderHistory() {
        if (this.history.length === 0) {
            this.historyList.innerHTML = `
                <div class="history-empty">
                    <p>No recent expansions. Start by entering a URL above.</p>
                </div>
            `;
            return;
        }

        this.historyList.innerHTML = this.history.map(item => `
            <div class="history-item" data-id="${item.id}">
                <div class="history-urls">
                    <div class="history-original">${this.escapeHtml(item.original)}</div>
                    <div class="history-final">${this.escapeHtml(item.final)}</div>
                </div>
                <div class="history-time">${this.formatTime(item.timestamp)}</div>
            </div>
        `).join('');

        // Add click handlers for history items
        this.historyList.querySelectorAll('.history-item').forEach(item => {
            item.addEventListener('click', () => {
                const id = parseInt(item.dataset.id);
                const historyItem = this.history.find(h => h.id === id);
                if (historyItem) {
                    this.urlInput.value = historyItem.original;
                    this.validateInput();
                }
            });
        });
    }

    clearHistory() {
        if (confirm('Are you sure you want to clear all history?')) {
            this.history = [];
            this.saveHistory();
            this.renderHistory();
            this.showNotification('History cleared', 'success');
        }
    }

    // Modal management
    showModal() {
        this.aboutModal.classList.remove('hidden');
        document.body.style.overflow = 'hidden';
    }

    hideModal() {
        this.aboutModal.classList.add('hidden');
        document.body.style.overflow = '';
    }

    // Utility methods
    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    formatTime(timestamp) {
        const date = new Date(timestamp);
        const now = new Date();
        const diffMs = now - date;
        const diffMins = Math.floor(diffMs / 60000);
        const diffHours = Math.floor(diffMins / 60);
        const diffDays = Math.floor(diffHours / 24);

        if (diffMins < 1) return 'Just now';
        if (diffMins < 60) return `${diffMins}m ago`;
        if (diffHours < 24) return `${diffHours}h ago`;
        if (diffDays < 7) return `${diffDays}d ago`;
        
        return date.toLocaleDateString();
    }

    showNotification(message, type = 'info') {
        // Create notification element
        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;
        notification.textContent = message;
        
        // Style the notification
        Object.assign(notification.style, {
            position: 'fixed',
            top: '20px',
            right: '20px',
            padding: '12px 20px',
            borderRadius: '8px',
            color: 'white',
            fontWeight: '500',
            zIndex: '10000',
            transform: 'translateX(100%)',
            transition: 'transform 0.3s ease-in-out',
            maxWidth: '300px',
            wordWrap: 'break-word'
        });

        // Set background color based on type
        const colors = {
            success: '#10b981',
            error: '#ef4444',
            warning: '#f59e0b',
            info: '#3b82f6'
        };
        notification.style.backgroundColor = colors[type] || colors.info;

        // Add to page
        document.body.appendChild(notification);

        // Animate in
        setTimeout(() => {
            notification.style.transform = 'translateX(0)';
        }, 100);

        // Remove after delay
        setTimeout(() => {
            notification.style.transform = 'translateX(100%)';
            setTimeout(() => {
                if (notification.parentNode) {
                    notification.parentNode.removeChild(notification);
                }
            }, 300);
        }, 3000);
    }
}

// Initialize the application when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new URLXpandaApp();
});

// Service Worker registration disabled - uncomment when sw.js is available
// if ('serviceWorker' in navigator) {
//     window.addEventListener('load', () => {
//         navigator.serviceWorker.register('/sw.js')
//             .then(registration => {
//                 console.log('SW registered: ', registration);
//             })
//             .catch(registrationError => {
//                 console.log('SW registration failed: ', registrationError);
//             });
//     });
// }
