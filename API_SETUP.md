# Google Safe Browsing API Setup

## Quick Start

### 1. Get API Key

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing
3. Enable "Safe Browsing API"
4. Create API credentials → API Key
5. Copy the API key

### 2. Add to Render

1. Go to your Render dashboard
2. Select URLXpanda service
3. Environment tab → Add Environment Variable
4. Key: `GOOGLE_SAFE_BROWSING_API_KEY`
5. Value: Your API key
6. Save (auto-redeploys)

### 3. Test

Expand any URL - you'll now see real threat detection!

## What You Get

### With API Key ✅
- Real-time threat detection
- Google's threat database
- Malware, phishing, unwanted software detection
- 10,000 free requests/day
- Safety score = 0 for confirmed threats

### Without API Key ⚠️
- Pattern matching only (HTTPS, TLDs, keywords)
- No real threat database
- Still works, just less accurate

## API Details

**Endpoint**: `https://safebrowsing.googleapis.com/v5alpha1/urls:search`

**Threat Types Checked**:
- MALWARE
- SOCIAL_ENGINEERING (phishing)
- UNWANTED_SOFTWARE
- POTENTIALLY_HARMFUL_APPLICATION

**Rate Limits**:
- 10,000 requests/day (free)
- 1,000 requests/100 seconds

## How It Works

1. User expands URL
2. Backend checks Google Safe Browsing API (if key configured)
3. If threat found → Safety score = 0, show critical warning
4. If safe or API unavailable → Pattern matching fallback
5. Results displayed with source attribution

## Privacy

- Uses v5alpha1 `urls.search` method
- Sends actual URLs to Google (not hashed)
- Google's IP privacy: Only for networking & anti-DoS
- Optional: Use Oblivious HTTP Gateway for full IP privacy

## Local Development

```bash
export GOOGLE_SAFE_BROWSING_API_KEY="your-key-here"
cd web
python3 serve.py
```

## Troubleshooting

**API not working?**
- Check API key is correct
- Verify Safe Browsing API is enabled in Google Cloud
- Check Render environment variables
- Look at server logs for error messages

**Still shows pattern matching?**
- API key not set or invalid
- API quota exceeded
- Network issue (falls back gracefully)

## Cost

**Free Tier**: 10,000 requests/day - plenty for most use cases

**Paid**: Contact Google Cloud for higher limits

## More Info

- [Google Safe Browsing v5 Docs](https://developers.google.com/safe-browsing/v5)
- [API Reference](https://developers.google.com/safe-browsing/v5/reference/rest)
