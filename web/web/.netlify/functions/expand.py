import json
import urllib.request
import urllib.parse
from urllib.parse import urlparse
import time

def handler(event, context):
    query_params = event.get('queryStringParameters', {})
    url = query_params.get('url')
    
    if not url:
        return {
            'statusCode': 400,
            'body': json.dumps({'error': 'Missing URL parameter'})
        }
    
    if not url.startswith(('http://', 'https://')):
        return {
            'statusCode': 400,
            'body': json.dumps({'error': 'Invalid URL format'})
        }
    
    try:
        start_time = time.time()
        result = expand_url(url)
        result['expansion_time_ms'] = int((time.time() - start_time) * 1000)
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
                'Access-Control-Allow-Headers': 'Content-Type'
            },
            'body': json.dumps(result)
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }

def expand_url(url):
    current_url = url
    redirect_chain = []
    redirect_chain.append({
        'url': url,
        'status_code': 0,
        'is_final': False
    })
    
    class NoRedirectHandler(urllib.request.HTTPRedirectHandler):
        def redirect_request(self, req, fp, code, msg, headers, newurl):
            return None
    
    opener = urllib.request.build_opener(NoRedirectHandler)
    opener.addheaders = [('User-Agent', 'Mozilla/5.0 (URLXpanda) AppleWebKit/537.36')]
    
    for i in range(10):
        try:
            req = urllib.request.Request(current_url)
            req.add_header('User-Agent', 'Mozilla/5.0 (URLXpanda) AppleWebKit/537.36')
            
            response = opener.open(req, timeout=10)
            status_code = response.getcode()
            
            if redirect_chain:
                redirect_chain[-1]['status_code'] = status_code
                redirect_chain[-1]['is_final'] = True
            break
            
        except urllib.error.HTTPError as e:
            status_code = e.code
            
            if redirect_chain:
                redirect_chain[-1]['status_code'] = status_code
            
            if 300 <= status_code < 400:
                location = e.headers.get('Location')
                if location:
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
            
            if redirect_chain:
                redirect_chain[-1]['is_final'] = True
            break
            
        except Exception as e:
            if redirect_chain:
                redirect_chain[-1]['status_code'] = 0
                redirect_chain[-1]['is_final'] = True
            break
    
    if redirect_chain and not any(hop['is_final'] for hop in redirect_chain):
        redirect_chain[-1]['is_final'] = True
    
    return {
        'original_url': url,
        'final_url': current_url,
        'redirect_chain': redirect_chain
    }
