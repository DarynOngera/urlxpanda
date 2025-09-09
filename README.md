# URLXpanda 🔗

A powerful, multi-platform URL expansion tool built with Rust that safely expands shortened URLs and provides rich link previews with safety indicators.

[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy)

## 🌟 Features

- **🚀 Fast URL Expansion**: Expand shortened URLs from 15+ popular services (bit.ly, tinyurl, t.co, etc.)
- **🛡️ Safety First**: HTTPS/HTTP indicators, suspicious domain warnings, and redirect chain analysis
- **📱 Multi-Platform**: CLI tool, web app, browser extension, and mobile app (Android/iOS)
- **🎨 Rich Previews**: Open Graph metadata with titles, descriptions, and images
- **🔒 Privacy-Focused**: Client-side processing option with local backend
- **⚡ Built with Rust**: High performance and memory safety
- **🌙 Modern UI**: Dark mode support and responsive design

## 🚀 Quick Start

### Web App (Deployed on Render)

Visit **[urlxpanda.onrender.com](https://urlxpanda.onrender.com)** to use URLXpanda instantly in your browser.

### Local Development

```bash
# Clone the repository
git clone https://github.com/DarynOngera/urlxpanda.git
cd urlxpanda

# Build and run the web app
cd web
./build.sh
python3 serve.py

# Open http://localhost:8000
```

## 📦 Installation Options

### 1. Browser Extension

#### Chrome/Chromium
1. Download or clone this repository
2. Open Chrome and navigate to `chrome://extensions/`
3. Enable "Developer mode" (toggle in top right)
4. Click "Load unpacked" and select the `extension/` folder
5. The URLXpanda extension will appear in your toolbar

#### Firefox
1. Download or clone this repository
2. Open Firefox and navigate to `about:debugging`
3. Click "This Firefox" in the sidebar
4. Click "Load Temporary Add-on"
5. Select the `manifest.json` file from the `extension/` folder

**Extension Features:**
- 🔗 Automatically detects shortened URLs on any webpage
- 💡 Hover tooltips with rich previews
- 🎯 Right-click context menu integration
- ⚙️ Customizable settings (auto-expand, previews, safety warnings)
- 📋 One-click copy functionality

### 2. Command Line Interface

```bash
# Install Rust if you haven't already
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh

# Build and install the CLI
cargo install --path crates/urlxpanda-cli

# Use the CLI
urlxpanda-cli https://bit.ly/example
```

### 3. Mobile App (Android/iOS)

```bash
# Prerequisites: Android Studio + NDK or Xcode
cargo install tauri-cli
cd mobile

# Android
cargo tauri android build

# iOS (macOS only)
cargo tauri ios build
```

## 🏗️ Architecture

URLXpanda is built as a Rust workspace with multiple components:

```
urlxpanda/
├── crates/
│   ├── urlxpanda-lib/     # Core Rust library
│   ├── urlxpanda-cli/     # Command-line interface
│   └── urlxpanda-wasm/    # WebAssembly module
├── web/                   # Web application
├── extension/             # Browser extension
├── mobile/                # Mobile app (Tauri + egui)
└── README.md
```

### Core Library (`urlxpanda-lib`)
- Async URL expansion with configurable timeouts
- Manual redirect following for better control
- Built with `reqwest` and `tokio`

### Web App (`web/`)
- **Frontend**: Rust WebAssembly + Modern JavaScript
- **Backend**: Python server with URL expansion API
- **Features**: Rich previews, history, settings, dark mode

### Browser Extension (`extension/`)
- **Content Script**: Detects and expands URLs in-place
- **Background Script**: Handles API communication
- **Popup Interface**: Manual expansion and settings

### Mobile App (`mobile/`)
- **Framework**: Tauri (Rust backend) + egui (native UI)
- **Platforms**: Android and iOS
- **Features**: Touch-optimized interface, native performance

## 🌐 Deployment

### Deploy to Render

1. Fork this repository
2. Connect your GitHub account to [Render](https://render.com)
3. Create a new Web Service
4. Connect your forked repository
5. Use these settings:
   - **Build Command**: `cd web && ./build.sh`
   - **Start Command**: `cd web && python3 serve.py`
   - **Environment**: Python 3

### Manual Deployment

```bash
# Build the web app
cd web && ./build.sh

# Deploy the web/ directory to any static hosting service
# Ensure CORS headers are configured for WASM files
```

### Environment Variables

For production deployment, you can configure:

```bash
PORT=8000                    # Server port
CORS_ORIGIN=*               # CORS origin policy
MAX_REDIRECTS=10            # Maximum redirect hops
REQUEST_TIMEOUT=10          # Request timeout in seconds
```

## 🔧 Development

### Prerequisites

- **Rust** 1.70+ with Cargo
- **wasm-pack** (for WebAssembly builds)
- **Python 3.8+** (for development server)
- **Node.js 16+** (optional, for alternative serving)

### Building Components

```bash
# Build CLI
cargo build --release -p urlxpanda-cli

# Build WASM module
cd web && ./build.sh

# Build mobile app
cd mobile && cargo tauri build

# Run tests
cargo test --workspace
```

### Development Workflow

1. **Start the backend server**:
   ```bash
   cd web && python3 serve.py
   ```

2. **Make changes to Rust code**:
   ```bash
   # Rebuild WASM after changes
   cd web && ./build.sh
   ```

3. **Test the browser extension**:
   - Load unpacked extension in Chrome/Firefox
   - Test on pages with shortened URLs

## 🛡️ Security & Privacy

- **Client-Side Processing**: Core expansion logic runs in your browser
- **No External Dependencies**: No third-party tracking or analytics
- **Local Storage**: History and settings stored locally
- **HTTPS Preferred**: Warns about insecure HTTP connections
- **Suspicious Domain Detection**: Flags potentially malicious shorteners

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Add tests if applicable
5. Commit your changes (`git commit -m 'Add amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

### Development Guidelines

- Follow Rust naming conventions and formatting (`cargo fmt`)
- Add documentation for public APIs
- Write tests for new functionality
- Update README for significant changes

## 📊 Supported URL Shorteners

- bit.ly, tinyurl.com, goo.gl, t.co
- short.link, ow.ly, buff.ly, is.gd
- tiny.cc, url.ie, v.gd, qr.ae
- cutt.ly, rebrand.ly, linktr.ee
- And many more...

## 🐛 Troubleshooting

### Browser Extension Issues
- **Extension not loading**: Check if developer mode is enabled
- **URLs not expanding**: Verify the backend server is running
- **Previews not showing**: Check browser console for CORS errors

### Web App Issues
- **WASM errors**: Rebuild with `./build.sh` and refresh
- **API errors**: Ensure backend server is running on port 8000
- **Blank page**: Check browser console for JavaScript errors

### Mobile App Issues
- **Build failures**: Verify Android SDK/NDK or Xcode installation
- **Runtime crashes**: Check device logs and permissions

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built with [Rust](https://www.rust-lang.org/) and [WebAssembly](https://webassembly.org/)
- UI powered by modern CSS and vanilla JavaScript
- Mobile app built with [Tauri](https://tauri.app/) and [egui](https://github.com/emilk/egui)
- Deployed on [Render](https://render.com/)

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/DarynOngera/urlxpanda/issues)
- **Discussions**: [GitHub Discussions](https://github.com/DarynOngera/urlxpanda/discussions)
- **Blog**: [ongeradaryn.blog](https://ongeradaryn.blog/about)

---

<div align="center">
  <p>Made with ❤️ by <a href="https://ongeradaryn.blog/about">Daryn Ongera</a></p>
  <p>
    <a href="https://github.com/DarynOngera/urlxpanda">⭐ Star this project</a> •
    <a href="https://github.com/DarynOngera/urlxpanda/issues">🐛 Report Bug</a> •
    <a href="https://github.com/DarynOngera/urlxpanda/discussions">💬 Request Feature</a>
  </p>
</div>
