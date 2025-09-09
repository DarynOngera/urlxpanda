// URLXpanda Browser Extension - Content Script
class URLXpandaContent {
  constructor() {
    this.settings = {};
    this.expandedUrls = new Map();
    this.tooltips = new Map();
    this.init();
  }

  async init() {
    // Load settings
    this.settings = await this.getSettings();
    
    // Initialize URL detection
    this.setupUrlDetection();
    
    // Listen for messages from background script
    chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
      this.handleMessage(message, sender, sendResponse);
    });
    
    console.log('URLXpanda content script initialized');
  }

  async getSettings() {
    return new Promise((resolve) => {
      chrome.runtime.sendMessage({ action: 'getSettings' }, (response) => {
        resolve(response || {});
      });
    });
  }

  setupUrlDetection() {
    // Find all links on the page
    this.scanForLinks();
    
    // Watch for dynamically added links
    const observer = new MutationObserver((mutations) => {
      mutations.forEach((mutation) => {
        mutation.addedNodes.forEach((node) => {
          if (node.nodeType === Node.ELEMENT_NODE) {
            this.scanElement(node);
          }
        });
      });
    });
    
    observer.observe(document.body, {
      childList: true,
      subtree: true
    });
  }

  scanForLinks() {
    const links = document.querySelectorAll('a[href]');
    links.forEach(link => this.processLink(link));
  }

  scanElement(element) {
    if (element.tagName === 'A' && element.href) {
      this.processLink(element);
    }
    
    const links = element.querySelectorAll('a[href]');
    links.forEach(link => this.processLink(link));
  }

  processLink(link) {
    const url = link.href;
    
    // Check if this is a shortened URL
    if (this.isShortenedUrl(url)) {
      this.addLinkIndicator(link);
      
      if (this.settings.expandOnHover) {
        this.addHoverExpansion(link);
      }
      
      if (this.settings.autoExpand) {
        this.expandLinkInBackground(link);
      }
    }
  }

  isShortenedUrl(url) {
    const shortenedDomains = [
      'bit.ly', 'tinyurl.com', 'goo.gl', 't.co', 'short.link',
      'ow.ly', 'buff.ly', 'is.gd', 'tiny.cc', 'url.ie',
      'v.gd', 'qr.ae', 'cutt.ly', 'rebrand.ly', 'linktr.ee'
    ];
    
    try {
      const domain = new URL(url).hostname.toLowerCase();
      return shortenedDomains.some(shortDomain => 
        domain === shortDomain || domain.endsWith('.' + shortDomain)
      );
    } catch {
      return false;
    }
  }

  addLinkIndicator(link) {
    // Add visual indicator for shortened URLs
    if (link.querySelector('.urlxpanda-indicator')) return;
    
    const indicator = document.createElement('span');
    indicator.className = 'urlxpanda-indicator';
    indicator.innerHTML = '🔗';
    indicator.title = 'Shortened URL - Click to expand';
    
    link.appendChild(indicator);
    
    // Add click handler for manual expansion
    indicator.addEventListener('click', (e) => {
      e.preventDefault();
      e.stopPropagation();
      this.expandLink(link);
    });
  }

  addHoverExpansion(link) {
    let hoverTimeout;
    
    link.addEventListener('mouseenter', () => {
      hoverTimeout = setTimeout(() => {
        this.showLinkPreview(link);
      }, 500);
    });
    
    link.addEventListener('mouseleave', () => {
      clearTimeout(hoverTimeout);
      this.hideLinkPreview(link);
    });
  }

  async expandLinkInBackground(link) {
    const url = link.href;
    
    if (this.expandedUrls.has(url)) return;
    
    try {
      const result = await this.expandUrl(url);
      this.expandedUrls.set(url, result);
      this.updateLinkWithResult(link, result);
    } catch (error) {
      console.error('URLXpanda: Failed to expand URL in background:', error);
    }
  }

  async expandLink(link) {
    const url = link.href;
    
    // Show loading state
    this.showLoadingState(link);
    
    try {
      const result = await this.expandUrl(url);
      this.expandedUrls.set(url, result);
      this.showExpansionResult(link, result);
    } catch (error) {
      this.showExpansionError(link, error.message);
    }
  }

  async expandUrl(url) {
    return new Promise((resolve, reject) => {
      chrome.runtime.sendMessage(
        { action: 'expandUrl', url: url },
        (response) => {
          if (response.success) {
            resolve(response.data);
          } else {
            reject(new Error(response.error));
          }
        }
      );
    });
  }

  updateLinkWithResult(link, result) {
    // Update link appearance based on expansion result
    const indicator = link.querySelector('.urlxpanda-indicator');
    if (indicator) {
      if (result.final_url !== result.original_url) {
        indicator.innerHTML = '✅';
        indicator.title = `Expands to: ${result.final_url}`;
        
        // Add safety indicator
        if (result.metadata?.is_safe) {
          const safety = result.metadata.is_safe;
          if (!safety.is_https || safety.is_suspicious) {
            indicator.innerHTML = '⚠️';
            indicator.style.color = '#f59e0b';
          }
        }
      }
    }
  }

  showLinkPreview(link) {
    const url = link.href;
    const result = this.expandedUrls.get(url);
    
    if (!result) {
      this.expandLink(link);
      return;
    }
    
    this.createTooltip(link, result);
  }

  createTooltip(link, result) {
    const tooltip = document.createElement('div');
    tooltip.className = 'urlxpanda-tooltip';
    
    const metadata = result.metadata;
    const title = metadata?.title || 'No title available';
    const description = metadata?.description || 'No description available';
    const image = metadata?.image;
    const domain = metadata?.is_safe?.domain || new URL(result.final_url).hostname;
    
    tooltip.innerHTML = `
      <div class="urlxpanda-tooltip-header">
        <span class="urlxpanda-tooltip-domain">${domain}</span>
        ${metadata?.is_safe?.is_https ? 
          '<span class="urlxpanda-https-badge">🔒 HTTPS</span>' : 
          '<span class="urlxpanda-http-badge">⚠️ HTTP</span>'
        }
      </div>
      <div class="urlxpanda-tooltip-content">
        ${image ? `<img src="${image}" class="urlxpanda-tooltip-image" alt="Preview">` : ''}
        <div class="urlxpanda-tooltip-text">
          <h4 class="urlxpanda-tooltip-title">${this.escapeHtml(title)}</h4>
          <p class="urlxpanda-tooltip-description">${this.escapeHtml(description)}</p>
          <div class="urlxpanda-tooltip-url">${result.final_url}</div>
        </div>
      </div>
    `;
    
    // Position tooltip
    const rect = link.getBoundingClientRect();
    tooltip.style.position = 'fixed';
    tooltip.style.top = `${rect.bottom + 10}px`;
    tooltip.style.left = `${rect.left}px`;
    tooltip.style.zIndex = '10000';
    
    document.body.appendChild(tooltip);
    this.tooltips.set(link, tooltip);
  }

  hideLinkPreview(link) {
    const tooltip = this.tooltips.get(link);
    if (tooltip) {
      tooltip.remove();
      this.tooltips.delete(link);
    }
  }

  showLoadingState(link) {
    const indicator = link.querySelector('.urlxpanda-indicator');
    if (indicator) {
      indicator.innerHTML = '⏳';
      indicator.title = 'Expanding URL...';
    }
  }

  showExpansionResult(link, result) {
    this.updateLinkWithResult(link, result);
    
    // Show notification
    this.showNotification(`URL expanded: ${result.final_url}`, 'success');
  }

  showExpansionError(link, error) {
    const indicator = link.querySelector('.urlxpanda-indicator');
    if (indicator) {
      indicator.innerHTML = '❌';
      indicator.title = `Failed to expand: ${error}`;
    }
    
    this.showNotification(`Failed to expand URL: ${error}`, 'error');
  }

  showNotification(message, type) {
    const notification = document.createElement('div');
    notification.className = `urlxpanda-notification urlxpanda-notification-${type}`;
    notification.textContent = message;
    
    notification.style.position = 'fixed';
    notification.style.top = '20px';
    notification.style.right = '20px';
    notification.style.zIndex = '10001';
    
    document.body.appendChild(notification);
    
    setTimeout(() => {
      notification.remove();
    }, 3000);
  }

  handleMessage(message, sender, sendResponse) {
    switch (message.action) {
      case 'showExpansionResult':
        const link = document.querySelector(`a[href="${message.originalUrl}"]`);
        if (link) {
          this.showExpansionResult(link, message.result);
        }
        break;
        
      case 'showExpansionError':
        const errorLink = document.querySelector(`a[href="${message.originalUrl}"]`);
        if (errorLink) {
          this.showExpansionError(errorLink, message.error);
        }
        break;
    }
  }

  escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
  }
}

// Initialize when DOM is ready
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', () => {
    new URLXpandaContent();
  });
} else {
  new URLXpandaContent();
}
