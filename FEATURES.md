# URLXpanda Features

## 🆕 New Features (Latest Update)

### 1. 🧹 URL Cleaning & Sanitization

Automatically removes tracking parameters from URLs to protect your privacy.

#### Supported Tracking Parameters (30+):

**Google Analytics:**
- `utm_source`, `utm_medium`, `utm_campaign`, `utm_term`, `utm_content`

**Facebook:**
- `fbclid`, `fb_action_ids`, `fb_action_types`, `fb_source`, `fb_ref`

**Google Ads:**
- `gclid`, `gclsrc`, `dclid`

**Microsoft/Bing:**
- `msclkid`

**Email Marketing:**
- `mc_cid`, `mc_eid` (Mailchimp)
- `_hsenc`, `_hsmi`, `__hssc`, `__hstc`, `__hsfp`, `hsCtaTracking` (HubSpot)
- `mkt_tok` (Marketo)

**Social Media:**
- `twclid` (Twitter)
- `li_fat_id` (LinkedIn)
- `igshid`, `igsh` (Instagram)
- `tt_medium`, `tt_content` (TikTok)

**Other:**
- `_ga`, `_gl`, `affiliate_id`, `click_id`, `ref`, `referrer`, `source`, `campaign`

#### How It Works:

1. **Automatic Detection**: When you expand a URL, URLXpanda automatically detects tracking parameters
2. **Clean Display**: Shows both original and cleaned versions side-by-side
3. **One-Click Copy**: Copy the cleaned URL with a single click
4. **Transparency**: See exactly which parameters were removed

#### Example:

**Original URL:**
```
https://example.com/page?utm_source=twitter&utm_medium=social&fbclid=abc123&product=shoes
```

**Cleaned URL:**
```
https://example.com/page?product=shoes
```

**Removed Parameters:** `utm_source`, `utm_medium`, `fbclid`

---

### 2. 🛡️ Enhanced Safety Scoring

Advanced URL reputation system with detailed security analysis.

#### Safety Score (0-100):

- **80-100**: 🟢 **Safe** - Low risk, proceed with confidence
- **50-79**: 🟡 **Caution** - Medium risk, review warnings
- **0-49**: 🔴 **High Risk** - Dangerous, avoid clicking

#### Scoring Factors:

| Factor | Impact | Description |
|--------|--------|-------------|
| **No HTTPS** | -30 points | Unencrypted connection |
| **URL Shortener** | -20 points | Known shortener domain |
| **Malicious Pattern** | -40 points | Suspicious keywords detected |
| **Suspicious TLD** | -15 points | High-risk domain extension |
| **IP Address** | -25 points | Uses IP instead of domain |
| **Excessive Subdomains** | -10 points | Potential phishing indicator |

#### Security Checks:

1. **HTTPS Verification**
   - Checks if the URL uses secure HTTPS protocol
   - Warns about unencrypted HTTP connections

2. **Domain Reputation**
   - Identifies known URL shorteners (18+ services)
   - Detects suspicious domain patterns

3. **Malicious Pattern Detection**
   - Scans for phishing keywords: `phishing`, `malware`, `virus`, `hack`, `crack`
   - Identifies urgent/scam patterns: `free-download`, `urgent-update`, `verify-account`

4. **TLD Analysis**
   - Flags suspicious top-level domains: `.tk`, `.ml`, `.ga`, `.cf`, `.gq`, `.xyz`, `.top`, `.work`
   - These TLDs are commonly associated with spam/malicious content

5. **IP Address Detection**
   - Identifies URLs using IP addresses instead of domain names
   - Both IPv4 and IPv6 supported

6. **Subdomain Analysis**
   - Counts subdomain levels
   - Flags excessive subdomains (>3) as potential phishing

#### Warning Severity Levels:

- 🚨 **High**: Critical security risk (malicious patterns)
- ⚠️ **Medium**: Significant concern (no HTTPS, suspicious TLD, IP address)
- ℹ️ **Low**: Minor issue (URL shortener, excessive subdomains)

#### Example Output:

```
Safety Score: 45/100 🔴 High Risk

Security Warnings:
🚨 High: URL contains patterns commonly associated with phishing or malware
⚠️ Medium: This URL uses HTTP instead of HTTPS - your connection is not encrypted
⚠️ Medium: Domain uses a TLD commonly associated with spam or malicious content
```

---

## 🎯 Core Features

### URL Expansion
- Expand shortened URLs from 15+ popular services
- Follow redirect chains up to 10 hops
- Display complete redirect path with status codes

### Rich Link Previews
- Open Graph metadata extraction
- Page titles and descriptions
- Preview images
- Site name detection

### Redirect Chain Visualization
- Visual representation of all redirects
- HTTP status codes for each hop
- Domain highlighting

### History Management
- Store last 50 expansions
- Quick re-expansion from history
- Timestamp tracking
- Local storage persistence

### Privacy-Focused
- No data sent to external servers (except target URL)
- Client-side processing with WASM
- No logging or tracking
- Open source and transparent

---

## 🚀 Usage Examples

### Example 1: Social Media Link

**Input:**
```
https://t.co/abc123?utm_source=twitter
```

**Output:**
- **Original**: `https://t.co/abc123?utm_source=twitter`
- **Final**: `https://example.com/article?id=456&utm_source=twitter`
- **Cleaned**: `https://example.com/article?id=456`
- **Safety Score**: 70/100 (Caution - URL shortener)
- **Removed**: `utm_source`

### Example 2: Marketing Email Link

**Input:**
```
https://example.com/promo?mc_cid=abc&mc_eid=def&utm_campaign=summer
```

**Output:**
- **Cleaned**: `https://example.com/promo`
- **Safety Score**: 100/100 (Safe)
- **Removed**: `mc_cid`, `mc_eid`, `utm_campaign`

### Example 3: Suspicious URL

**Input:**
```
http://192.168.1.1/verify-account?urgent=true
```

**Output:**
- **Safety Score**: 15/100 (High Risk)
- **Warnings**:
  - 🚨 URL contains patterns commonly associated with phishing
  - ⚠️ Uses HTTP instead of HTTPS
  - ⚠️ URL uses an IP address instead of a domain name

---

## 📊 Statistics

### Tracking Parameters Removed
URLXpanda can detect and remove **30+ different tracking parameters** from:
- Google (Analytics, Ads)
- Facebook
- Twitter
- LinkedIn
- Instagram
- TikTok
- Email marketing platforms (Mailchimp, HubSpot, Marketo)
- And more...

### URL Shorteners Detected
Recognizes **18+ URL shortening services**:
- bit.ly, tinyurl.com, goo.gl, t.co
- ow.ly, is.gd, buff.ly, adf.ly
- bc.vc, soo.gd, clicky.me, s2r.co
- db.tt, qr.ae, cutt.ly, rb.gy, short.io
- bit.do

---

## 🔒 Privacy & Security

### What We Check:
✅ HTTPS encryption  
✅ Domain reputation  
✅ Malicious patterns  
✅ Suspicious TLDs  
✅ IP addresses  
✅ Subdomain structure  

### What We DON'T Do:
❌ Store your URLs  
❌ Track your activity  
❌ Send data to third parties  
❌ Require registration  
❌ Use cookies for tracking  

---

## 🎨 User Interface

### Visual Indicators:

**Safety Score Bar:**
- Green (80-100): Safe to proceed
- Orange (50-79): Review warnings
- Red (0-49): High risk, avoid

**Cleaned URL Section:**
- Before/after comparison
- Highlighted removed parameters
- One-click copy button
- Expandable parameter list

**Warning Cards:**
- Color-coded by severity
- Clear, actionable messages
- Icon indicators
- Detailed explanations

---

## 🛠️ Technical Details

### Backend (Python)
- `clean_url()`: Removes tracking parameters
- `check_safety()`: Calculates safety score
- `generate_safety_warnings()`: Creates detailed alerts
- `is_ip_address()`: Detects IP-based URLs

### Frontend (JavaScript)
- `generateCleanedUrlHTML()`: Displays cleaned URLs
- `generateSafetyIndicatorsHTML()`: Shows safety score
- Copy-to-clipboard functionality
- Responsive design

### Performance
- Instant URL cleaning (< 1ms)
- Safety scoring (< 5ms)
- No external API calls for scoring
- Efficient regex-based detection

---

## 📱 Platform Support

- ✅ Web App (all modern browsers)
- ✅ Browser Extension (Chrome, Firefox, Brave)
- ✅ Mobile App (Android, iOS via Tauri)
- ✅ CLI Tool (command line)

---

## 🔄 Future Enhancements

### Planned Features:
- [ ] Integration with VirusTotal API
- [ ] Google Safe Browsing API
- [ ] PhishTank database lookup
- [ ] Custom tracking parameter lists
- [ ] Whitelist/blacklist domains
- [ ] Export safety reports
- [ ] Batch URL processing
- [ ] QR code generation
- [ ] Screenshot capture

---

## 📚 Learn More

- [Deployment Guide](./DEPLOYMENT.md)
- [Migration Guide](./RAILWAY_TO_RENDER_MIGRATION.md)
- [README](./README.md)
- [GitHub Repository](https://github.com/DarynOngera/urlxpanda)

---

**Built with ❤️ using Rust, Python, and WebAssembly**
