# Testing Google Safe Browsing API

## Quick Test

### 1. Set Your API Key

```bash
export GOOGLE_SAFE_BROWSING_API_KEY="your-api-key-here"
```

### 2. Run Test Script

```bash
python3 test_safe_browsing.py
```

## What the Test Does

The test script checks:

### ✅ Direct API Tests (v5alpha1)
- Tests Google's official malware test URL
- Tests phishing test URL
- Tests unwanted software URL
- Tests safe URLs (example.com, google.com)

### ✅ Fallback API Tests (v4)
- Verifies v4 API works as fallback
- Tests malware and safe URLs

### ✅ Backend Integration Tests
- Tests URLXpanda's `/api/expand` endpoint
- Verifies Google Safe Browsing integration
- Checks safety scoring
- Validates warning messages

## Test URLs Used

These are official Google test URLs:

| URL | Expected Result |
|-----|----------------|
| `http://malware.testing.google.test/testing/malware/` | MALWARE detected |
| `http://testsafebrowsing.appspot.com/s/phishing.html` | PHISHING detected |
| `http://testsafebrowsing.appspot.com/s/unwanted.html` | UNWANTED SOFTWARE |
| `https://example.com` | SAFE |
| `https://www.google.com` | SAFE |

## Expected Output (With API Key)

```
============================================================
Google Safe Browsing API Test Suite
============================================================

✓ API Key found: AIzaSyBOT...xyz

============================================================
TESTING GOOGLE SAFE BROWSING API v5alpha1
============================================================

============================================================
Testing: malware
URL: http://malware.testing.google.test/testing/malware/
============================================================

📡 Making API request to v5alpha1...
✓ Response Status: 200
✓ Response JSON: {...}
⚠️  Result: THREAT DETECTED

[... more tests ...]

============================================================
TEST SUMMARY
============================================================

v5alpha1 API Tests: 5/5 passed
v4 API Tests: 2/2 passed
Backend Tests: 5/5 passed

============================================================
✓ ALL TESTS PASSED!
```

## Manual Testing

### Test Direct API (v5alpha1)

```bash
# Set your API key
export API_KEY="your-key-here"

# Test with Google's malware test URL
curl "https://safebrowsing.googleapis.com/v5alpha1/urls:search?key=$API_KEY&urls=http%3A%2F%2Fmalware.testing.google.test%2Ftesting%2Fmalware%2F"
```

**Expected:** Response with threat information or empty for safe URLs

### Test Direct API (v4)

```bash
curl -X POST \
  "https://safebrowsing.googleapis.com/v4/threatMatches:find?key=$API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "client": {
      "clientId": "urlxpanda",
      "clientVersion": "1.0.0"
    },
    "threatInfo": {
      "threatTypes": ["MALWARE", "SOCIAL_ENGINEERING"],
      "platformTypes": ["ANY_PLATFORM"],
      "threatEntryTypes": ["URL"],
      "threatEntries": [
        {"url": "http://malware.testing.google.test/testing/malware/"}
      ]
    }
  }'
```

**Expected:** JSON with `matches` array containing threat info

### Test URLXpanda Backend

```bash
# Make sure server is running
cd web && python3 serve.py

# In another terminal, test the endpoint
curl "http://localhost:8000/api/expand?url=http://malware.testing.google.test/testing/malware/" | jq .
```

**Expected:** JSON response with:
- `metadata.is_safe.google_safe_browsing` object
- `metadata.is_safe.safety_score` = 0 (for threats)
- `metadata.is_safe.warnings` with critical severity

## Troubleshooting

### API Key Not Working

**Check:**
1. API key is correct (no spaces)
2. Safe Browsing API is enabled in Google Cloud Console
3. API key restrictions allow Safe Browsing API

**Test API key:**
```bash
curl "https://safebrowsing.googleapis.com/v5alpha1/urls:search?key=$API_KEY&urls=https://example.com"
```

If you get `403 Forbidden`, the API is not enabled or key is invalid.

### Backend Not Detecting Threats

**Check:**
1. Environment variable is set: `echo $GOOGLE_SAFE_BROWSING_API_KEY`
2. Server was restarted after setting env var
3. Check server logs for API errors

**Verify in response:**
```bash
curl "http://localhost:8000/api/expand?url=https://example.com" | jq '.metadata.is_safe.google_safe_browsing'
```

Should show:
```json
{
  "is_safe": true,
  "threats": [],
  "source": "Google Safe Browsing v5",
  "api_version": "v5alpha1"
}
```

If `null`, API key is not set or API call failed.

### Rate Limiting

**Free tier limits:**
- 10,000 requests/day
- 1,000 requests/100 seconds

**Check quota:**
- Go to Google Cloud Console
- APIs & Services → Dashboard
- Select Safe Browsing API
- View quotas

## Continuous Testing

### Add to CI/CD

```yaml
# .github/workflows/test.yml
- name: Test Safe Browsing API
  env:
    GOOGLE_SAFE_BROWSING_API_KEY: ${{ secrets.GOOGLE_SAFE_BROWSING_API_KEY }}
  run: python3 test_safe_browsing.py
```

### Local Development

```bash
# Add to .env
GOOGLE_SAFE_BROWSING_API_KEY=your-key-here

# Run tests before committing
python3 test_safe_browsing.py
```

## Success Criteria

✅ **All tests should pass:**
- v5alpha1 API detects test malware/phishing URLs
- v4 API works as fallback
- Backend integrates API results correctly
- Safety scores reflect threat level
- Warnings include Google Safe Browsing source

✅ **Performance:**
- API responses < 5 seconds
- Graceful fallback if API unavailable
- Pattern matching works without API key

✅ **Security:**
- API key not exposed in logs
- HTTPS used for API calls
- Proper error handling

## Next Steps

After successful testing:

1. **Deploy to Render**
   - Add API key to Render environment variables
   - Verify deployment logs show API integration

2. **Monitor Usage**
   - Check Google Cloud Console for API usage
   - Set up alerts for quota limits
   - Monitor error rates

3. **User Testing**
   - Test with real shortened URLs
   - Verify threat detection in production
   - Check UI displays threat warnings correctly

## Support

- [Google Safe Browsing Docs](https://developers.google.com/safe-browsing)
- [API Setup Guide](./API_SETUP.md)
- [Environment Config](./ENVIRONMENT.md)
