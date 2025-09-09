#!/bin/bash

# URLXpanda WASM Build Script for Netlify
set -e

echo "🔧 Building URLXpanda WASM Frontend for Netlify..."

# Check if wasm-pack is installed
if ! command -v wasm-pack &> /dev/null; then
    echo "❌ wasm-pack is not installed. Installing..."
    curl https://rustwasm.github.io/wasm-pack/installer/init.sh -sSf | sh
fi

# Navigate to project root (from web directory)
cd "$(dirname "$0")/.."

echo "📦 Building WASM package..."
wasm-pack build crates/urlxpanda-wasm --target web --out-dir ../../web/pkg --no-typescript

echo "🧹 Cleaning up unnecessary files..."
cd web
rm -f pkg/.gitignore pkg/package.json pkg/README.md

# Create _redirects file for SPA routing
cat > _redirects << 'EOF'
/api/* /.netlify/functions/:splat 200
/api/expand /.netlify/functions/expand 200
/* /index.html 200
EOF

echo "✅ Build completed successfully!"
echo ""
echo "🚀 Ready for Netlify deployment!"
echo ""
echo "📦 Files generated:"
echo "   - pkg/urlxpanda_wasm.js (WASM bindings)"
echo "   - pkg/urlxpanda_wasm_bg.wasm (WASM module)"
echo "   - _redirects (SPA routing rules)"
