// URLXpanda Browser Extension - Background Script
const API_BASE = 'https://urlxpanda-production.up.railway.app/api';

// Create context menu on installation
chrome.runtime.onInstalled.addListener(() => {
  chrome.contextMenus.create({
    id: 'expandUrl',
    title: 'Expand URL with URLXpanda',
    contexts: ['link']
  });
});

// Handle context menu clicks
chrome.contextMenus.onClicked.addListener((info, tab) => {
  if (info.menuItemId === 'expandUrl' && info.linkUrl) {
    expandUrlInPlace(info.linkUrl, tab.id);
  }
});

// Handle messages from content script
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.action === 'expandUrl') {
    expandUrl(request.url)
      .then(result => sendResponse({ success: true, data: result }))
      .catch(error => sendResponse({ success: false, error: error.message }));
    return true; // Keep message channel open for async response
  }
  
  if (request.action === 'getSettings') {
    chrome.storage.sync.get({
      autoExpand: true,
      showPreviews: true,
      safetyWarnings: true,
      expandOnHover: true,
      blacklistedDomains: []
    }, (settings) => {
      sendResponse(settings);
    });
    return true;
  }
  
  if (request.action === 'saveSettings') {
    chrome.storage.sync.set(request.settings, () => {
      sendResponse({ success: true });
    });
    return true;
  }
});

// Expand URL using local API
async function expandUrl(url) {
  try {
    const response = await fetch(`${API_BASE}/expand?url=${encodeURIComponent(url)}`);
    
    if (!response.ok) {
      throw new Error(`API returned ${response.status}: ${response.statusText}`);
    }
    
    const data = await response.json();
    return data;
  } catch (error) {
    console.error('URLXpanda: Failed to expand URL:', error);
    throw error;
  }
}

// Expand URL and notify content script
async function expandUrlInPlace(url, tabId) {
  try {
    const result = await expandUrl(url);
    
    chrome.tabs.sendMessage(tabId, {
      action: 'showExpansionResult',
      originalUrl: url,
      result: result
    });
  } catch (error) {
    chrome.tabs.sendMessage(tabId, {
      action: 'showExpansionError',
      originalUrl: url,
      error: error.message
    });
  }
}

// Handle extension icon click
chrome.action.onClicked.addListener((tab) => {
  // Open popup is handled by manifest, this is backup
  chrome.action.openPopup();
});
