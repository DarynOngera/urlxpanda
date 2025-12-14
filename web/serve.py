#!/usr/bin/env python3
"""
URLXpanda server with URL expansion proxy
"""
import http.server
import socketserver
import json
import urllib.request
import urllib.parse
import urllib.error
from http.server import SimpleHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import time
import os
from pathlib import Path

# Load environment variables from .env file if it exists
def load_env_file():
    """Load environment variables from .env file"""
    env_file = Path(__file__).parent / '.env'
    if env_file.exists():
        print(f"📄 Loading environment variables from {env_file}")
        with open(env_file, 'r') as f:
            for line in f:
                line = line.strip()
                # Skip comments and empty lines
                if line and not line.startswith('#'):
                    # Parse KEY=VALUE format
                    if '=' in line:
                        key, value = line.split('=', 1)
                        key = key.strip()
                        value = value.strip()
                        # Remove quotes if present
                        if value.startswith('"') and value.endswith('"'):
                            value = value[1:-1]
                        elif value.startswith("'") and value.endswith("'"):
                            value = value[1:-1]
                        # Only set if not already in environment
                        if key not in os.environ:
                            os.environ[key] = value
                            print(f"  ✓ Loaded: {key}")
    else:
        print(f"ℹ️  No .env file found at {env_file}")

# Load .env file at startup
load_env_file()

class URLXpandaHandler(SimpleHTTPRequestHandler):
    def end_headers(self):
        
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        super().end_headers()
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.end_headers()
    
    def do_GET(self):
        parsed_path = urlparse(self.path)
        
        if parsed_path.path == '/api/expand':
            self.handle_expand_url(parsed_path)
        else:
            # Serve static files
            super().do_GET()
    
    def handle_expand_url(self, parsed_path):
        try:
            query_params = parse_qs(parsed_path.query)
            url = query_params.get('url', [None])[0]
            
            if not url:
                self.send_error_response(400, "Missing URL parameter")
                return
            
            # Validate URL format
            if not url.startswith(('http://', 'https://')):
                self.send_error_response(400, "Invalid URL format")
                return
            
            start_time = time.time()
            result = self.expand_url(url)
            expansion_time = int((time.time() - start_time) * 1000)
            
            result['expansion_time_ms'] = expansion_time
            
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(result).encode())
            
        except Exception as e:
            print(f"Error expanding URL: {e}")
            self.send_error_response(500, f"Error expanding URL: {str(e)}")
    
    def expand_url(self, url, max_redirects=10):
        """Expand URL by following redirects manually and extract metadata"""
        current_url = url
        redirect_chain = []
        
        # Add initial URL
        redirect_chain.append({
            'url': url,
            'status_code': 0,
            'is_final': False
        })
        
        # Use GET request to follow redirects and get content
        class NoRedirectHandler(urllib.request.HTTPRedirectHandler):
            def redirect_request(self, req, fp, code, msg, headers, newurl):
                return None
        
        opener = urllib.request.build_opener(NoRedirectHandler)
        opener.addheaders = [('User-Agent', 'Mozilla/5.0 (URLXpanda) AppleWebKit/537.36')]
        
        for i in range(max_redirects):
            try:
                req = urllib.request.Request(current_url)
                req.add_header('User-Agent', 'Mozilla/5.0 (URLXpanda) AppleWebKit/537.36')
                
                try:
                    response = opener.open(req, timeout=10)
                    status_code = response.getcode()
                    
                    # Update current hop with status code
                    if redirect_chain:
                        redirect_chain[-1]['status_code'] = status_code
                        redirect_chain[-1]['is_final'] = True
                    break
                    
                except urllib.error.HTTPError as e:
                    status_code = e.code
                    
                    # Update current hop with status code
                    if redirect_chain:
                        redirect_chain[-1]['status_code'] = status_code
                    
                    # Check if it's a redirect
                    if 300 <= status_code < 400:
                        location = e.headers.get('Location')
                        if location:
                            # Resolve relative URLs
                            if location.startswith('/'):
                                parsed = urlparse(current_url)
                                location = f"{parsed.scheme}://{parsed.netloc}{location}"
                            elif not location.startswith(('http://', 'https://')):
                                location = urllib.parse.urljoin(current_url, location)
                            
                            redirect_chain.append({
                                'url': location,
                                'status_code': 0,
                                'is_final': False
                            })
                            
                            current_url = location
                            continue
                    
                    # Not a redirect, mark as final
                    if redirect_chain:
                        redirect_chain[-1]['is_final'] = True
                    break
                    
            except Exception as e:
                print(f"Error following redirect {i+1}: {e}")
                if redirect_chain:
                    redirect_chain[-1]['status_code'] = 0
                    redirect_chain[-1]['is_final'] = True
                break
        
        # Ensure at least one hop is marked as final
        if redirect_chain and not any(hop['is_final'] for hop in redirect_chain):
            redirect_chain[-1]['is_final'] = True
        
        # Extract metadata from final URL
        metadata = self.extract_metadata(current_url)
        
        # Clean the final URL
        cleaned_info = self.clean_url(current_url)
        
        return {
            'original_url': url,
            'final_url': current_url,
            'redirect_chain': redirect_chain,
            'metadata': metadata,
            'cleaned_url': cleaned_info['cleaned_url'],
            'removed_tracking_params': cleaned_info['removed_params'],
            'has_tracking': cleaned_info['is_cleaned']
        }
    
    def extract_metadata(self, url):
        """Extract metadata from the final URL"""
        try:
            req = urllib.request.Request(url)
            req.add_header('User-Agent', 'Mozilla/5.0 (URLXpanda) AppleWebKit/537.36')
            
            with urllib.request.urlopen(req, timeout=10) as response:
                content = response.read().decode('utf-8', errors='ignore')
                
                metadata = {
                    'title': self.extract_title(content),
                    'description': self.extract_description(content),
                    'image': self.extract_image(content, url),
                    'site_name': self.extract_site_name(content),
                    'content_type': response.headers.get('Content-Type', ''),
                    'is_safe': self.check_safety(url),
                }
                
                return metadata
                
        except Exception as e:
            print(f"Error extracting metadata: {e}")
            return {
                'title': None,
                'description': None,
                'image': None,
                'site_name': None,
                'content_type': None,
                'is_safe': self.check_safety(url),
            }
    
    def extract_title(self, content):
        """Extract page title"""
        import re
        # Try Open Graph title first
        og_title = re.search(r'<meta\s+property=["\']og:title["\']\s+content=["\']([^"\']*)["\']', content, re.IGNORECASE)
        if og_title:
            return og_title.group(1)
        
        # Try regular title tag
        title = re.search(r'<title[^>]*>([^<]*)</title>', content, re.IGNORECASE)
        if title:
            return title.group(1).strip()
        
        return None
    
    def extract_description(self, content):
        """Extract page description"""
        import re
        # Try Open Graph description
        og_desc = re.search(r'<meta\s+property=["\']og:description["\']\s+content=["\']([^"\']*)["\']', content, re.IGNORECASE)
        if og_desc:
            return og_desc.group(1)
        
        # Try meta description
        meta_desc = re.search(r'<meta\s+name=["\']description["\']\s+content=["\']([^"\']*)["\']', content, re.IGNORECASE)
        if meta_desc:
            return meta_desc.group(1)
        
        return None
    
    def extract_image(self, content, base_url):
        """Extract page image"""
        import re
        # Try Open Graph image
        og_image = re.search(r'<meta\s+property=["\']og:image["\']\s+content=["\']([^"\']*)["\']', content, re.IGNORECASE)
        if og_image:
            image_url = og_image.group(1)
            if image_url.startswith('/'):
                parsed = urlparse(base_url)
                return f"{parsed.scheme}://{parsed.netloc}{image_url}"
            return image_url
        
        return None
    
    def extract_site_name(self, content):
        """Extract site name"""
        import re
        # Try Open Graph site name
        og_site = re.search(r'<meta\s+property=["\']og:site_name["\']\s+content=["\']([^"\']*)["\']', content, re.IGNORECASE)
        if og_site:
            return og_site.group(1)
        
        return None
    
    def clean_url(self, url):
        """Remove tracking parameters from URL"""
        try:
            parsed = urlparse(url)
            
            # Common tracking parameters to remove
            tracking_params = {
                # Google Analytics
                'utm_source', 'utm_medium', 'utm_campaign', 'utm_term', 'utm_content',
                # Facebook
                'fbclid', 'fb_action_ids', 'fb_action_types', 'fb_source', 'fb_ref',
                # Google Ads
                'gclid', 'gclsrc', 'dclid',
                # Microsoft/Bing
                'msclkid',
                # Mailchimp
                'mc_cid', 'mc_eid',
                # HubSpot
                '_hsenc', '_hsmi', '__hssc', '__hstc', '__hsfp', 'hsCtaTracking',
                # Marketo
                'mkt_tok',
                # Adobe
                's_cid',
                # Twitter
                'twclid',
                # LinkedIn
                'li_fat_id',
                # Instagram
                'igshid', 'igsh',
                # TikTok
                'tt_medium', 'tt_content',
                # Other common tracking
                'ref', 'referrer', 'source', 'campaign',
                '_ga', '_gl', 'affiliate_id', 'click_id'
            }
            
            # Parse query parameters
            from urllib.parse import parse_qs, urlencode
            query_params = parse_qs(parsed.query, keep_blank_values=True)
            
            # Remove tracking parameters
            cleaned_params = {
                key: value for key, value in query_params.items() 
                if key.lower() not in tracking_params
            }
            
            # Rebuild query string
            cleaned_query = urlencode(cleaned_params, doseq=True) if cleaned_params else ''
            
            # Reconstruct URL
            cleaned_url = urllib.parse.urlunparse((
                parsed.scheme,
                parsed.netloc,
                parsed.path,
                parsed.params,
                cleaned_query,
                parsed.fragment
            ))
            
            return {
                'cleaned_url': cleaned_url,
                'removed_params': list(set(query_params.keys()) - set(cleaned_params.keys())),
                'is_cleaned': len(cleaned_params) < len(query_params)
            }
        except Exception as e:
            print(f"Error cleaning URL: {e}")
            return {
                'cleaned_url': url,
                'removed_params': [],
                'is_cleaned': False
            }
    
    def check_google_safe_browsing(self, url):
        """Check URL against Google Safe Browsing API v5alpha1"""
        api_key = os.environ.get('GOOGLE_SAFE_BROWSING_API_KEY')
        
        if not api_key:
            return None  # API key not configured
        
        try:
            # Use v5alpha1 urls.search method (simpler, sends actual URLs)
            # URL encode the URL parameter
            encoded_url = urllib.parse.quote(url, safe='')
            api_url = f'https://safebrowsing.googleapis.com/v5alpha1/urls:search?key={api_key}&urls={encoded_url}'
            
            req = urllib.request.Request(api_url)
            
            with urllib.request.urlopen(req, timeout=5) as response:
                # Response is protocol buffer, but we'll parse as JSON for simplicity
                content = response.read()
                
                # Try to parse as JSON (some responses may be JSON)
                try:
                    result = json.loads(content.decode('utf-8'))
                except:
                    # If not JSON, check if response is empty (safe)
                    if not content or len(content) == 0:
                        return {
                            'is_safe': True,
                            'threats': [],
                            'source': 'Google Safe Browsing v5',
                            'api_version': 'v5alpha1'
                        }
                    # Otherwise, assume it's protobuf and we can't parse it easily
                    # Fall back to v4 API
                    return self.check_google_safe_browsing_v4(url)
                
                # Parse v5 response
                if 'threat' in result or 'threats' in result:
                    # Threat detected
                    threat_data = result.get('threat', result.get('threats', {}))
                    threats = []
                    
                    if isinstance(threat_data, dict):
                        # Single threat object
                        threat_types = threat_data.get('threatTypes', [])
                        for threat_type in threat_types:
                            threats.append({
                                'type': threat_type,
                                'platform': 'ANY_PLATFORM'
                            })
                    elif isinstance(threat_data, list):
                        # Array of threats
                        for threat in threat_data:
                            threat_types = threat.get('threatTypes', [threat.get('threatType', 'UNKNOWN')])
                            if isinstance(threat_types, str):
                                threat_types = [threat_types]
                            for threat_type in threat_types:
                                threats.append({
                                    'type': threat_type,
                                    'platform': 'ANY_PLATFORM'
                                })
                    
                    return {
                        'is_safe': False,
                        'threats': threats,
                        'source': 'Google Safe Browsing v5',
                        'api_version': 'v5alpha1'
                    }
                else:
                    # No threats found
                    return {
                        'is_safe': True,
                        'threats': [],
                        'source': 'Google Safe Browsing v5',
                        'api_version': 'v5alpha1'
                    }
                    
        except urllib.error.HTTPError as e:
            if e.code == 404:
                # URL not found in threat lists (safe)
                return {
                    'is_safe': True,
                    'threats': [],
                    'source': 'Google Safe Browsing v5',
                    'api_version': 'v5alpha1'
                }
            print(f"Google Safe Browsing API HTTP error: {e.code} - {e.reason}")
            # Fall back to v4 API
            return self.check_google_safe_browsing_v4(url)
        except Exception as e:
            print(f"Google Safe Browsing API error: {e}")
            # Try v4 API as fallback
            return self.check_google_safe_browsing_v4(url)
    
    def check_google_safe_browsing_v4(self, url):
        """Fallback to Google Safe Browsing API v4"""
        api_key = os.environ.get('GOOGLE_SAFE_BROWSING_API_KEY')
        
        if not api_key:
            return None
        
        try:
            api_url = f'https://safebrowsing.googleapis.com/v4/threatMatches:find?key={api_key}'
            
            payload = {
                "client": {
                    "clientId": "urlxpanda",
                    "clientVersion": "1.0.0"
                },
                "threatInfo": {
                    "threatTypes": [
                        "MALWARE",
                        "SOCIAL_ENGINEERING",
                        "UNWANTED_SOFTWARE",
                        "POTENTIALLY_HARMFUL_APPLICATION"
                    ],
                    "platformTypes": ["ANY_PLATFORM"],
                    "threatEntryTypes": ["URL"],
                    "threatEntries": [
                        {"url": url}
                    ]
                }
            }
            
            req = urllib.request.Request(
                api_url,
                data=json.dumps(payload).encode('utf-8'),
                headers={'Content-Type': 'application/json'}
            )
            
            with urllib.request.urlopen(req, timeout=5) as response:
                result = json.loads(response.read().decode('utf-8'))
                
                if 'matches' in result and result['matches']:
                    threats = []
                    for match in result['matches']:
                        threat_type = match.get('threatType', 'UNKNOWN')
                        threats.append({
                            'type': threat_type,
                            'platform': match.get('platformType', 'UNKNOWN')
                        })
                    
                    return {
                        'is_safe': False,
                        'threats': threats,
                        'source': 'Google Safe Browsing v4',
                        'api_version': 'v4'
                    }
                else:
                    return {
                        'is_safe': True,
                        'threats': [],
                        'source': 'Google Safe Browsing v4',
                        'api_version': 'v4'
                    }
                    
        except Exception as e:
            print(f"Google Safe Browsing v4 API error: {e}")
            return None
    
    def check_safety(self, url):
        """Enhanced safety check with Google Safe Browsing and pattern matching"""
        parsed = urlparse(url)
        
        # Check Google Safe Browsing first
        gsb_result = self.check_google_safe_browsing(url)
        
        # Check for HTTPS
        is_https = parsed.scheme == 'https'
        
        # Expanded list of suspicious/shortener domains
        suspicious_domains = [
            'bit.do', 'tinyurl.com', 'goo.gl', 't.co', 'ow.ly', 'bit.ly',
            'is.gd', 'buff.ly', 'adf.ly', 'bc.vc', 'soo.gd', 'clicky.me',
            's2r.co', 'db.tt', 'qr.ae', 'cutt.ly', 'rb.gy', 'short.io'
        ]
        
        # Check for known malicious patterns
        malicious_patterns = [
            'phishing', 'malware', 'virus', 'hack', 'crack',
            'free-download', 'urgent-update', 'verify-account'
        ]
        
        # Check domain reputation
        domain = parsed.netloc.lower()
        is_suspicious = any(susp_domain in domain for susp_domain in suspicious_domains)
        has_malicious_pattern = any(pattern in url.lower() for pattern in malicious_patterns)
        
        # Check for suspicious TLDs
        suspicious_tlds = ['.tk', '.ml', '.ga', '.cf', '.gq', '.xyz', '.top', '.work']
        has_suspicious_tld = any(domain.endswith(tld) for tld in suspicious_tlds)
        
        # Check for IP address instead of domain
        is_ip_address = self.is_ip_address(domain)
        
        # Check for excessive subdomains (potential phishing)
        subdomain_count = domain.count('.')
        has_excessive_subdomains = subdomain_count > 3
        
        # Calculate safety score (0-100, higher is safer)
        safety_score = 100
        
        # Google Safe Browsing takes priority
        if gsb_result and not gsb_result['is_safe']:
            safety_score = 0  # Confirmed threat
            has_confirmed_threat = True
        else:
            has_confirmed_threat = False
            
            if not is_https:
                safety_score -= 30
            if is_suspicious:
                safety_score -= 20
            if has_malicious_pattern:
                safety_score -= 40
            if has_suspicious_tld:
                safety_score -= 15
            if is_ip_address:
                safety_score -= 25
            if has_excessive_subdomains:
                safety_score -= 10
        
        # Ensure score is between 0 and 100
        safety_score = max(0, min(100, safety_score))
        
        # Determine risk level
        if safety_score >= 80:
            risk_level = 'low'
        elif safety_score >= 50:
            risk_level = 'medium'
        else:
            risk_level = 'high'
        
        return {
            'is_https': is_https,
            'is_suspicious': is_suspicious,
            'domain': parsed.netloc,
            'safety_score': safety_score,
            'risk_level': risk_level,
            'google_safe_browsing': gsb_result,
            'has_confirmed_threat': has_confirmed_threat,
            'warnings': self.generate_safety_warnings(
                is_https, is_suspicious, has_malicious_pattern, 
                has_suspicious_tld, is_ip_address, has_excessive_subdomains,
                gsb_result
            )
        }
    
    def is_ip_address(self, domain):
        """Check if domain is an IP address"""
        import re
        # Simple IPv4 check
        ipv4_pattern = r'^(\d{1,3}\.){3}\d{1,3}$'
        # Simple IPv6 check
        ipv6_pattern = r'^([0-9a-fA-F]{0,4}:){2,7}[0-9a-fA-F]{0,4}$'
        return bool(re.match(ipv4_pattern, domain) or re.match(ipv6_pattern, domain))
    
    def generate_safety_warnings(self, is_https, is_suspicious, has_malicious_pattern, 
                                  has_suspicious_tld, is_ip_address, has_excessive_subdomains,
                                  gsb_result=None):
        """Generate list of safety warnings"""
        warnings = []
        
        # Google Safe Browsing threats (highest priority)
        if gsb_result and not gsb_result['is_safe']:
            for threat in gsb_result['threats']:
                threat_type = threat['type']
                
                # Map threat types to user-friendly messages
                threat_messages = {
                    'MALWARE': 'This URL is flagged for distributing malware',
                    'SOCIAL_ENGINEERING': 'This URL is flagged as a phishing or social engineering site',
                    'UNWANTED_SOFTWARE': 'This URL may distribute unwanted software',
                    'POTENTIALLY_HARMFUL_APPLICATION': 'This URL may contain potentially harmful applications'
                }
                
                warnings.append({
                    'type': 'google_safe_browsing',
                    'severity': 'critical',
                    'message': threat_messages.get(threat_type, f'Threat detected: {threat_type}'),
                    'source': 'Google Safe Browsing'
                })
        
        if not is_https:
            warnings.append({
                'type': 'no_https',
                'severity': 'medium',
                'message': 'This URL uses HTTP instead of HTTPS - your connection is not encrypted'
            })
        
        if is_suspicious:
            warnings.append({
                'type': 'url_shortener',
                'severity': 'low',
                'message': 'This is a known URL shortener domain'
            })
        
        if has_malicious_pattern:
            warnings.append({
                'type': 'malicious_pattern',
                'severity': 'high',
                'message': 'URL contains patterns commonly associated with phishing or malware'
            })
        
        if has_suspicious_tld:
            warnings.append({
                'type': 'suspicious_tld',
                'severity': 'medium',
                'message': 'Domain uses a TLD commonly associated with spam or malicious content'
            })
        
        if is_ip_address:
            warnings.append({
                'type': 'ip_address',
                'severity': 'medium',
                'message': 'URL uses an IP address instead of a domain name'
            })
        
        if has_excessive_subdomains:
            warnings.append({
                'type': 'excessive_subdomains',
                'severity': 'low',
                'message': 'URL has many subdomains, which may indicate phishing'
            })
        
        return warnings
    
    def send_error_response(self, code, message):
        self.send_response(code)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        error_response = {'error': message}
        self.wfile.write(json.dumps(error_response).encode())

PORT = int(os.environ.get("PORT", 8000))
Handler = URLXpandaHandler

# Check if Google Safe Browsing API key is configured
api_key = os.environ.get('GOOGLE_SAFE_BROWSING_API_KEY')
if api_key:
    print(f"✅ Google Safe Browsing API: ENABLED (key: {api_key[:10]}...{api_key[-4:]})")
else:
    print("⚠️  Google Safe Browsing API: DISABLED (no API key set)")
    print("   Set GOOGLE_SAFE_BROWSING_API_KEY environment variable to enable")

with socketserver.TCPServer(("", PORT), Handler) as httpd:
    print(f"\n🚀 URLXpanda server running at http://localhost:{PORT}")
    print("📱 Open this URL in your browser to use URLXpanda")
    print(f"🔗 API endpoint: http://localhost:{PORT}/api/expand?url=<URL>")
    print("⏹️  Press Ctrl+C to stop the server\n")
    httpd.serve_forever()
