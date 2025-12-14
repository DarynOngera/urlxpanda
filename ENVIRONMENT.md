# Environment Configuration Guide

## Quick Setup

```bash
# Copy example file
cp .env.example .env

# Edit with your values
nano .env  # or vim, code, etc.
```

## Environment Variables

### Required (with defaults)

| Variable | Default | Description |
|----------|---------|-------------|
| `PORT` | `8000` | Server port |
| `CORS_ORIGIN` | `*` | CORS allowed origins |
| `MAX_REDIRECTS` | `10` | Max redirect hops to follow |
| `REQUEST_TIMEOUT` | `10` | HTTP request timeout (seconds) |
| `PYTHON_VERSION` | `3.11` | Python version for deployment |

### Optional

| Variable | Default | Description |
|----------|---------|-------------|
| `GOOGLE_SAFE_BROWSING_API_KEY` | None | Google Safe Browsing API key for real-time threat detection |

## Platform-Specific Setup

### Local Development

```bash
# Set environment variables
export GOOGLE_SAFE_BROWSING_API_KEY="your-key-here"
export PORT=8000

# Or use .env file
cp .env.example .env
# Edit .env with your values

# Run server
cd web
python3 serve.py
```

### Render

1. Dashboard → Your Service → Environment
2. Add environment variables:
   - `GOOGLE_SAFE_BROWSING_API_KEY` = your-key
   - Other variables (optional, defaults work)
3. Save (auto-redeploys)

### Docker

```bash
# Using environment file
docker run -p 8000:8000 --env-file .env urlxpanda

# Or inline
docker run -p 8000:8000 \
  -e GOOGLE_SAFE_BROWSING_API_KEY="your-key" \
  -e PORT=8000 \
  urlxpanda
```

### Netlify/Vercel (Frontend only)

These platforms host the static frontend. The backend needs to be deployed separately (e.g., on Render).

## Feature Flags

### With `GOOGLE_SAFE_BROWSING_API_KEY`
✅ Real-time threat detection  
✅ Google's malware/phishing database  
✅ 10,000 free requests/day  
✅ Safety score = 0 for confirmed threats  

### Without `GOOGLE_SAFE_BROWSING_API_KEY`
⚠️ Pattern matching only  
⚠️ HTTPS, TLD, keyword checking  
⚠️ No external API calls  
⚠️ Privacy-focused (no data sent to Google)  

## Security Best Practices

### ✅ DO
- Use `.env` files for local development
- Store API keys in platform environment variables
- Use different keys for dev/staging/production
- Rotate API keys periodically
- Monitor API usage in Google Cloud Console

### ❌ DON'T
- Commit `.env` files to git
- Hardcode API keys in source code
- Share API keys in chat/email
- Use production keys in development
- Expose API keys in client-side code

## Troubleshooting

### API Key Not Working

**Check:**
1. API key is correct (no extra spaces)
2. Safe Browsing API is enabled in Google Cloud
3. Environment variable name is exact: `GOOGLE_SAFE_BROWSING_API_KEY`
4. Server was restarted after adding env var
5. Check server logs for API errors

**Test:**
```bash
# Check if env var is set
echo $GOOGLE_SAFE_BROWSING_API_KEY

# Test API directly
curl "https://safebrowsing.googleapis.com/v5alpha1/urls:search?key=YOUR_KEY&urls=http://malware.testing.google.test/testing/malware/"
```

### Port Already in Use

```bash
# Find process using port
lsof -i :8000

# Kill process
kill -9 <PID>

# Or use different port
export PORT=8080
python3 serve.py
```

### CORS Issues

```bash
# Allow specific origin
export CORS_ORIGIN="https://yourdomain.com"

# Allow multiple origins (comma-separated)
export CORS_ORIGIN="https://app.com,https://www.app.com"

# Allow all (development only)
export CORS_ORIGIN="*"
```

## Validation

### Check Configuration

```python
# Run this in Python to check env vars
import os

print("PORT:", os.environ.get("PORT", "8000"))
print("CORS_ORIGIN:", os.environ.get("CORS_ORIGIN", "*"))
print("MAX_REDIRECTS:", os.environ.get("MAX_REDIRECTS", "10"))
print("API Key set:", "Yes" if os.environ.get("GOOGLE_SAFE_BROWSING_API_KEY") else "No")
```

### Test API Integration

Expand a known malware test URL:
```
http://malware.testing.google.test/testing/malware/
```

Expected result:
- Safety score: 0
- Risk level: High
- Warning: "This URL is flagged for distributing malware"
- Source: "Google Safe Browsing"

## More Information

- [API Setup Guide](./API_SETUP.md)
- [Google Safe Browsing Docs](https://developers.google.com/safe-browsing)
- [Deployment Guide](./DEPLOYMENT.md)
