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
        self.send_header('Cross-Origin-Embedder-Policy', 'require-corp')
        self.send_header('Cross-Origin-Opener-Policy', 'same-origin')
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
        
        return {
            'original_url': url,
            'final_url': current_url,
            'redirect_chain': redirect_chain,
            'metadata': metadata
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
    
    def check_safety(self, url):
        """Basic safety check"""
        parsed = urlparse(url)
        
        # Check for HTTPS
        is_https = parsed.scheme == 'https'
        
        # Check for suspicious domains (basic list)
        suspicious_domains = ['bit.do', 'tinyurl.com', 'goo.gl', 't.co']
        is_suspicious = any(domain in parsed.netloc for domain in suspicious_domains)
        
        return {
            'is_https': is_https,
            'is_suspicious': is_suspicious,
            'domain': parsed.netloc
        }
    
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
