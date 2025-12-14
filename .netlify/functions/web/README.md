# URLXpanda Web Frontend

A modern web interface for URL expansion built with Rust WebAssembly.

## Features

- 🚀 Fast WASM-powered URL expansion
- 🎨 Modern, responsive UI design
- 📱 Mobile-friendly interface
- 💾 Local history storage
- 🔒 Client-side processing (privacy-focused)
- ⚙️ Configurable settings
- 📋 One-click copy to clipboard
- 🌙 Dark mode support

## Quick Start

1. **Build the WASM module:**
   ```bash
   ./build.sh
   ```

2. **Start the development server:**
   ```bash
   python3 serve.py
   # or
   npm run serve
   ```

3. **Open your browser:**
   Navigate to `http://localhost:8000`

## Development

### Prerequisites

- Rust (latest stable)
- wasm-pack
- Python 3 or Node.js (for serving)

### Building

The build script will:
- Compile the Rust WASM module
- Generate JavaScript bindings
- Set up the web directory structure

### Serving

The included server scripts handle CORS headers required for WASM modules.

### Project Structure

```
web/
├── index.html          # Main HTML file
├── styles.css          # CSS styling
├── app.js             # JavaScript application
├── pkg/               # Generated WASM files
├── build.sh           # Build script
├── serve.py           # Development server
└── README.md          # This file
```

## Deployment

For production deployment:

1. Build the project: `./build.sh`
2. Serve the `web/` directory with any static file server
3. Ensure proper CORS headers for WASM files

### Example Nginx Configuration

```nginx
location / {
    add_header Cross-Origin-Embedder-Policy require-corp;
    add_header Cross-Origin-Opener-Policy same-origin;
    try_files $uri $uri/ /index.html;
}
```

## Browser Compatibility

- Chrome/Chromium 57+
- Firefox 52+
- Safari 11+
- Edge 16+

## Privacy

All URL expansion happens client-side in your browser. No data is sent to external servers.
