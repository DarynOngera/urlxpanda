#!/bin/bash

# URLXpanda WASM Build Script for Netlify
set -e

echo "🔧 Building URLXpanda WASM Frontend for Netlify..."

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

echo "✅ Build completed successfully!"
echo ""
echo "🚀 Ready for Netlify deployment!"
echo ""
echo "📦 WASM files generated in pkg/ directory"
