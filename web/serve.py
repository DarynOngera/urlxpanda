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
    
    def check_safety(self, url):
        """Enhanced safety check with reputation scoring"""
        parsed = urlparse(url)
        
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
            'warnings': self.generate_safety_warnings(
                is_https, is_suspicious, has_malicious_pattern, 
                has_suspicious_tld, is_ip_address, has_excessive_subdomains
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
                                  has_suspicious_tld, is_ip_address, has_excessive_subdomains):
        """Generate list of safety warnings"""
        warnings = []
        
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

import os

PORT = int(os.environ.get("PORT", 8000))
Handler = URLXpandaHandler

with socketserver.TCPServer(("", PORT), Handler) as httpd:
    print(f"🚀 URLXpanda server running at http://localhost:{PORT}")
    print("📱 Open this URL in your browser to use URLXpanda")
    print("🔗 API endpoint: http://localhost:{PORT}/api/expand?url=<URL>")
    print("⏹️  Press Ctrl+C to stop the server")
    httpd.serve_forever()
