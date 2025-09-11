// URLXpanda Browser Extension - Popup Script
class URLXpandaPopup {
  constructor() {
    this.settings = {};
    this.init();
  }

  async init() {
    // Load settings
    await this.loadSettings();
    
    // Setup event listeners
    this.setupEventListeners();
    
    // Focus URL input
    document.getElementById('urlInput').focus();
  }

  setupEventListeners() {
    // URL expansion
    document.getElementById('expandBtn').addEventListener('click', () => {
      this.expandUrl();
    });
    
    document.getElementById('urlInput').addEventListener('keypress', (e) => {
      if (e.key === 'Enter') {
        this.expandUrl();
      }
    });
    
    // Result actions
    document.getElementById('copyBtn').addEventListener('click', () => {
      this.copyFinalUrl();
    });
    
    document.getElementById('visitBtn').addEventListener('click', () => {
      this.visitPage();
    });
    
    // Settings
    document.getElementById('settingsBtn').addEventListener('click', () => {
      this.showSettings();
    });
    
    document.getElementById('closeSettings').addEventListener('click', () => {
      this.hideSettings();
    });
    
    document.getElementById('saveSettings').addEventListener('click', () => {
      this.saveSettings();
    });
    
    // Modal backdrop click
    document.getElementById('settingsModal').addEventListener('click', (e) => {
      if (e.target.id === 'settingsModal') {
        this.hideSettings();
      }
    });
  }

  async loadSettings() {
    this.settings = await new Promise((resolve) => {
      chrome.runtime.sendMessage({ action: 'getSettings' }, (response) => {
        if (chrome.runtime.lastError) {
          console.warn('URLXpanda: Could not connect to background script to get settings.');
          resolve({
            autoExpand: true,
            showPreviews: true,
            safetyWarnings: true,
            expandOnHover: true
          });
        } else {
resolve(response || {});
        }
      });
    });
    
    this.updateSettingsUI();
  }

  updateSettingsUI() {
    document.getElementById('autoExpand').checked = this.settings.autoExpand;
    document.getElementById('showPreviews').checked = this.settings.showPreviews;
    document.getElementById('expandOnHover').checked = this.settings.expandOnHover;
    document.getElementById('safetyWarnings').checked = this.settings.safetyWarnings;
  }

  async expandUrl() {
    const urlInput = document.getElementById('urlInput');
    const url = urlInput.value.trim();
    
    if (!url) {
      this.showError('Please enter a URL');
      return;
    }
    
    if (!this.isValidUrl(url)) {
      this.showError('Please enter a valid URL');
      return;
    }
    
    this.setLoadingState(true);
    this.hideResults();
    this.hideError();
    
    try {
      const result = await this.callExpandApi(url);
      this.showResult(result);
    } catch (error) {
      this.showError(error.message);
    } finally {
      this.setLoadingState(false);
    }
  }

  async callExpandApi(url) {
    return new Promise((resolve, reject) => {
      chrome.runtime.sendMessage(
        { action: 'expandUrl', url: url },
        (response) => {
          if (chrome.runtime.lastError) {
            reject(new Error(chrome.runtime.lastError.message));
          } else if (response.success) {
            resolve(response.data);
          } else {
            reject(new Error(response.error));
          }
        }
      );
    });
  }

  showResult(result) {
    // Update basic info
    document.getElementById('originalUrl').textContent = result.original_url;
    document.getElementById('finalUrl').textContent = result.final_url;
    document.getElementById('redirectCount').textContent = 
      `${result.redirect_chain.length - 1} redirect${result.redirect_chain.length - 1 !== 1 ? 's' : ''}`;
    document.getElementById('expansionTime').textContent = `${result.expansion_time_ms}ms`;
    
    // Show preview if metadata available
    if (result.metadata && this.settings.showPreviews) {
      this.showPreview(result.metadata, result.final_url);
    } else {
      this.hidePreview();
    }
    
    // Store result for actions
    this.currentResult = result;
    
    // Show result section
    document.getElementById('result').classList.remove('hidden');
  }

  showPreview(metadata, finalUrl) {
    const previewCard = document.getElementById('previewCard');
    
    const title = metadata.title || 'No title available';
    const description = metadata.description || 'No description available';
    const image = metadata.image;
    const safety = metadata.is_safe;
    
    let safetyHtml = '';
    if (this.settings.safetyWarnings && safety) {
      if (safety.is_https && !safety.is_suspicious) {
        safetyHtml = '<div class="safety-indicator safe">✅ Safe URL</div>';
      } else {
        const warnings = [];
        if (!safety.is_https) warnings.push('HTTP (not secure)');
        if (safety.is_suspicious) warnings.push('Suspicious domain');
        safetyHtml = `<div class="safety-indicator warning">⚠️ ${warnings.join(', ')}</div>`;
      }
    }
    
    previewCard.innerHTML = `
      ${safetyHtml}
      ${image ? `<img src="${image}" class="preview-image" alt="Preview">` : ''}
      <h4 class="preview-title">${this.escapeHtml(title)}</h4>
      <p class="preview-description">${this.escapeHtml(description)}</p>
    `;
    
    previewCard.classList.remove('hidden');
  }

  hidePreview() {
    document.getElementById('previewCard').classList.add('hidden');
  }

  showError(message) {
    const errorSection = document.getElementById('error');
    errorSection.querySelector('.error-message').textContent = message;
    errorSection.classList.remove('hidden');
  }

  hideError() {
    document.getElementById('error').classList.add('hidden');
  }

  hideResults() {
    document.getElementById('result').classList.add('hidden');
  }

  setLoadingState(loading) {
    const expandBtn = document.getElementById('expandBtn');
    const urlInput = document.getElementById('urlInput');
    
    expandBtn.disabled = loading;
    expandBtn.classList.toggle('loading', loading);
    urlInput.disabled = loading;
  }

  copyFinalUrl() {
    if (!this.currentResult) return;
    
    navigator.clipboard.writeText(this.currentResult.final_url).then(() => {
      this.showNotification('URL copied to clipboard!');
    }).catch(() => {
      // Fallback for older browsers
      const textArea = document.createElement('textarea');
      textArea.value = this.currentResult.final_url;
      document.body.appendChild(textArea);
      textArea.select();
      document.execCommand('copy');
      document.body.removeChild(textArea);
      this.showNotification('URL copied to clipboard!');
    });
  }

  visitPage() {
    if (!this.currentResult) return;
    
    chrome.tabs.create({ url: this.currentResult.final_url });
    window.close();
  }

  showSettings() {
    document.getElementById('settingsModal').classList.remove('hidden');
  }

  hideSettings() {
    document.getElementById('settingsModal').classList.add('hidden');
  }

  async saveSettings() {
    const newSettings = {
      autoExpand: document.getElementById('autoExpand').checked,
      showPreviews: document.getElementById('showPreviews').checked,
      expandOnHover: document.getElementById('expandOnHover').checked,
      safetyWarnings: document.getElementById('safetyWarnings').checked
    };
    
    await new Promise((resolve) => {
      chrome.runtime.sendMessage(
        { action: 'saveSettings', settings: newSettings },
        () => {
          if (chrome.runtime.lastError) {
            console.warn('URLXpanda: Could not connect to background script to save settings.');
          }
          resolve();
        }
      );
    });
    
    this.settings = newSettings;
    this.hideSettings();
    this.showNotification('Settings saved!');
  }

  showNotification(message) {
    // Simple notification - could be enhanced
    const notification = document.createElement('div');
    notification.textContent = message;
    notification.style.cssText = `
      position: fixed;
      top: 20px;
      right: 20px;
      background: #10b981;
      color: white;
      padding: 12px 16px;
      border-radius: 6px;
      font-size: 14px;
      z-index: 10000;
      animation: slideIn 0.3s ease-out;
    `;
    
    document.body.appendChild(notification);
    
    setTimeout(() => {
      notification.remove();
    }, 2000);
  }

  isValidUrl(string) {
    try {
      new URL(string);
      return true;
    } catch {
      return false;
    }
  }

  escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
  }
}

// Initialize popup when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
  new URLXpandaPopup();
});
