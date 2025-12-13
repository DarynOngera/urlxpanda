# URLXpanda Dockerfile for Render
# Multi-stage build for optimized image size

# Stage 1: Build WASM
FROM rust:1.75-slim as wasm-builder

# Install dependencies
RUN apt-get update && apt-get install -y \
    curl \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install wasm-pack
RUN curl https://rustwasm.github.io/wasm-pack/installer/init.sh -sSf | sh

# Set working directory
WORKDIR /app

# Copy workspace files
COPY Cargo.toml Cargo.lock ./
COPY crates ./crates

# Build WASM package
RUN wasm-pack build crates/urlxpanda-wasm --target web --out-dir ../../web/pkg --no-typescript

# Clean up unnecessary files
RUN cd web/pkg && rm -f .gitignore package.json README.md

# Stage 2: Runtime
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy web files
COPY web ./web

# Copy WASM build from previous stage
COPY --from=wasm-builder /app/web/pkg ./web/pkg

# Set working directory to web
WORKDIR /app/web

# Expose port (Render will override with PORT env var)
EXPOSE 10000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD python3 -c "import urllib.request; urllib.request.urlopen('http://localhost:${PORT:-10000}/')"

# Run the server
CMD ["python3", "serve.py"]
