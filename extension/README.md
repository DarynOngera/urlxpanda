# URLXpanda Browser Extension

A powerful browser extension that expands shortened URLs in-place and provides rich link previews with safety indicators.

## Features

- **In-Place URL Expansion**: Automatically detects and expands shortened URLs on web pages
- **Rich Link Previews**: Shows Open Graph metadata with titles, descriptions, and images
- **Safety Indicators**: Warns about HTTP vs HTTPS and suspicious domains
- **Hover Previews**: Optional tooltip previews when hovering over links
- **Context Menu Integration**: Right-click any link to expand it
- **Manual Expansion**: Popup interface for expanding specific URLs
- **Customizable Settings**: Configure auto-expansion, previews, and safety warnings

## Supported URL Shorteners

- bit.ly, tinyurl.com, goo.gl, t.co
- short.link, ow.ly, buff.ly, is.gd
- tiny.cc, url.ie, v.gd, qr.ae
- cutt.ly, rebrand.ly, linktr.ee
- And many more...

## Installation

### Chrome/Chromium
1. Open Chrome and navigate to `chrome://extensions/`
2. Enable "Developer mode" in the top right
3. Click "Load unpacked" and select the `extension` folder
4. The URLXpanda extension should now appear in your extensions list

### Firefox
1. Open Firefox and navigate to `about:debugging`
2. Click "This Firefox" in the sidebar
3. Click "Load Temporary Add-on"
4. Select the `manifest.json` file from the `extension` folder

## Setup

1. Make sure the URLXpanda server is running on `http://localhost:8000`
2. Start the server with: `cd web && python3 serve.py`
3. The extension will automatically connect to the local API

## Usage

### Automatic Mode
- The extension automatically scans pages for shortened URLs
- Shortened URLs are marked with a 🔗 indicator
- Click the indicator to expand the URL manually
- If auto-expansion is enabled, URLs are expanded in the background

### Manual Mode
- Click the URLXpanda extension icon in the toolbar
- Enter any URL in the popup to expand it
- View rich previews with metadata and safety information
- Copy the final URL or visit the page directly

### Context Menu
- Right-click any link on a webpage
- Select "Expand URL with URLXpanda" from the context menu
- The expansion result will be shown as a notification

### Hover Previews
- Enable "Expand on hover" in settings
- Hover over shortened URLs to see instant previews
- Previews include title, description, image, and safety info

## Settings

Access settings through the extension popup:

- **Auto-expand shortened URLs**: Automatically expand URLs in the background
- **Show link previews**: Display rich metadata previews
- **Expand on hover**: Show preview tooltips on hover
- **Safety warnings**: Display security and safety indicators

## API Integration

The extension connects to the URLXpanda backend API running on `localhost:8000`. The API provides:

- URL expansion with redirect following
- Open Graph metadata extraction
- Safety analysis (HTTPS, suspicious domains)
- Complete redirect chain tracking

## Privacy & Security

- All URL expansion happens locally through your own server
- No data is sent to external services
- URLs are processed through your local URLXpanda instance
- Safety warnings help identify potentially malicious links

## Development

### File Structure
```
extension/
├── manifest.json          # Extension manifest
├── background.js          # Background service worker
├── content.js            # Content script for page interaction
├── content.css           # Styles for page elements
├── popup.html            # Extension popup interface
├── popup.css             # Popup styles
├── popup.js              # Popup functionality
└── README.md             # This file
```

### Building
The extension is ready to use as-is. No build process required.

### Testing
1. Load the extension in developer mode
2. Navigate to a page with shortened URLs
3. Verify that URLs are detected and can be expanded
4. Test the popup interface and settings

## Troubleshooting

### Extension Not Working
- Ensure the URLXpanda server is running on `localhost:8000`
- Check browser console for error messages
- Verify extension permissions are granted

### URLs Not Expanding
- Check if the domain is in the supported shorteners list
- Verify network connectivity to localhost:8000
- Look for CORS or permission errors in console

### Previews Not Showing
- Enable "Show link previews" in settings
- Ensure the target website has Open Graph metadata
- Check for image loading restrictions

## Contributing

1. Fork the repository
2. Make your changes in the `extension/` directory
3. Test thoroughly in both Chrome and Firefox
4. Submit a pull request

## License

This project is part of the URLXpanda suite. See the main project for license information.
