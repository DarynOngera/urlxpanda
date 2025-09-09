#!/bin/bash

# URLXpanda WASM Build Script
set -e

echo "🔧 Building URLXpanda WASM Frontend..."

# Check if wasm-pack is installed
if ! command -v wasm-pack &> /dev/null; then
    echo "❌ wasm-pack is not installed. Installing..."
    curl https://rustwasm.github.io/wasm-pack/installer/init.sh -sSf | sh
fi

# Navigate to project root
cd "$(dirname "$0")/.."

echo "📦 Building WASM package..."
wasm-pack build crates/urlxpanda-wasm --target web --out-dir ../../web/pkg --no-typescript

echo "🧹 Cleaning up unnecessary files..."
cd web
rm -f pkg/.gitignore pkg/package.json pkg/README.md

echo "📝 Creating package.json for web frontend..."
cat > package.json << 'EOF'
{
  "name": "urlxpanda-web",
  "version": "0.1.0",
  "description": "URLXpanda Web Frontend",
  "main": "app.js",
  "scripts": {
    "build": "../build.sh",
    "serve": "python3 -m http.server 8000",
    "serve-node": "npx serve .",
    "dev": "python3 -m http.server 8000"
  },
  "keywords": ["url", "expansion", "wasm", "rust"],
  "author": "URLXpanda Team",
  "license": "MIT",
  "devDependencies": {
    "serve": "^14.0.0"
  }
}
EOF

echo "🌐 Creating development server script..."
cat > serve.py << 'EOF'
#!/usr/bin/env python3
"""
Simple HTTP server with CORS headers for WASM development
"""
import http.server
import socketserver
from http.server import SimpleHTTPRequestHandler

class CORSRequestHandler(SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header('Cross-Origin-Embedder-Policy', 'require-corp')
        self.send_header('Cross-Origin-Opener-Policy', 'same-origin')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        super().end_headers()

PORT = 8000
Handler = CORSRequestHandler

with socketserver.TCPServer(("", PORT), Handler) as httpd:
    print(f"🚀 Server running at http://localhost:{PORT}")
    print("📱 Open this URL in your browser to use URLXpanda")
    print("⏹️  Press Ctrl+C to stop the server")
    httpd.serve_forever()
EOF

chmod +x serve.py

echo "📋 Creating README for web frontend..."
cat > README.md << 'EOF'
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
EOF

echo "🔧 Creating .gitignore for web directory..."
cat > .gitignore << 'EOF'
# Generated WASM files
pkg/
node_modules/
*.log

# OS files
.DS_Store
Thumbs.db

# Editor files
.vscode/
.idea/
*.swp
*.swo
*~
EOF

echo "✅ Build completed successfully!"
echo ""
echo "🚀 To start the development server:"
echo "   cd web && python3 serve.py"
echo ""
echo "🌐 Then open: http://localhost:8000"
echo ""
echo "📦 Files generated:"
echo "   - pkg/urlxpanda_wasm.js (WASM bindings)"
echo "   - pkg/urlxpanda_wasm_bg.wasm (WASM module)"
echo "   - package.json (Node.js config)"
echo "   - serve.py (Development server)"
echo "   - README.md (Documentation)"
