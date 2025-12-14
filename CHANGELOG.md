# URLXpanda Changelog

## [Latest] - 2025-12-14

### Added
- **URL Cleaning/Sanitization Feature**
  - Removes 30+ tracking parameters (utm, fbclid, gclid, etc.)
  - User-controlled toggle switch (enabled by default)
  - Before/after URL comparison display
  - One-click copy cleaned URL button
  - Expandable list of removed parameters
  - Preference persists in localStorage

- **Enhanced Safety Scoring System**
  - 0-100 safety score with visual progress bar
  - Risk level classification (Low/Medium/High)
  - Color-coded indicators (green/orange/red)
  - Multiple security checks:
    - HTTPS verification
    - URL shortener detection (18+ services)
    - Malicious pattern detection
    - Suspicious TLD checking
    - IP address detection
    - Excessive subdomain analysis
  - Detailed security warnings with severity levels
  - Local analysis disclaimer message

### Changed
- Removed emojis from safety score bar for cleaner UI
- Made URL cleaning optional via toggle switch
- Updated safety score display to be more professional
- Added informational message about local security analysis
- Improved responsive design for new components

### UI Improvements
- Modern toggle switch component
- Clean safety score visualization
- Color-coded warning cards
- Collapsible parameter lists
- Better mobile responsiveness

### Technical Details
- **Backend (Python)**:
  - `clean_url()`: Sanitizes URLs by removing tracking parameters
  - `check_safety()`: Calculates comprehensive safety score
  - `generate_safety_warnings()`: Creates detailed security alerts
  - `is_ip_address()`: Detects IP-based URLs

- **Frontend (JavaScript)**:
  - `generateCleanedUrlHTML()`: Displays cleaned URLs conditionally
  - `generateSafetyIndicatorsHTML()`: Shows safety score and warnings
  - Toggle state management with localStorage
  - Copy-to-clipboard functionality

### Security & Privacy
- All security analysis performed locally on user's device
- No external API calls for safety scoring
- No tracking or data collection
- User preferences stored locally only

---

## Previous Updates

### Migration to Render
- Migrated deployment from Railway to Render
- Updated Dockerfile with Rust 1.83
- Fixed Cargo workspace configuration
- Updated all metadata URLs
- Created comprehensive deployment documentation

### Core Features
- URL expansion with redirect chain visualization
- Rich link previews with Open Graph metadata
- History management (last 50 expansions)
- Browser extension support
- CLI tool
- WASM-powered client-side processing

---

## Roadmap

### Planned Features
- [ ] Integration with VirusTotal API
- [ ] Google Safe Browsing API
- [ ] PhishTank database lookup
- [ ] Custom tracking parameter lists
- [ ] Whitelist/blacklist domains
- [ ] Export safety reports (PDF, CSV, JSON)
- [ ] Batch URL processing
- [ ] QR code generation
- [ ] Screenshot capture of destination pages
- [ ] Browser history scanning
- [ ] Collaborative features (teams, sharing)

### Future Enhancements
- [ ] Mobile app improvements
- [ ] API with authentication
- [ ] Analytics dashboard
- [ ] Dark/light theme toggle
- [ ] Bookmarklet
- [ ] Social media integration
- [ ] URL comparison tool

---

## Contributing

Contributions are welcome! Please see [README.md](./README.md) for guidelines.

## License

See [LICENSE](./LICENSE) file for details.

---

**Built with ❤️ using Rust, Python, and WebAssembly**
