#!/usr/bin/env python3
"""
Test script for Google Safe Browsing API integration
"""

import os
import sys
import json
import urllib.request
import urllib.parse
import urllib.error

# Test URLs provided by Google for testing
TEST_URLS = {
    'malware': 'http://malware.testing.google.test/testing/malware/',
    'phishing': 'http://testsafebrowsing.appspot.com/s/phishing.html',
    'unwanted': 'http://testsafebrowsing.appspot.com/s/unwanted.html',
    'safe': 'https://example.com',
    'safe_google': 'https://www.google.com',
}

def test_v5_api(api_key, url, url_name):
    """Test Google Safe Browsing API v5alpha1"""
    print(f"\n{'='*60}")
    print(f"Testing: {url_name}")
    print(f"URL: {url}")
    print(f"{'='*60}")
    
    try:
        # v5alpha1 urls.search method
        encoded_url = urllib.parse.quote(url, safe='')
        api_url = f'https://safebrowsing.googleapis.com/v5alpha1/urls:search?key={api_key}&urls={encoded_url}'
        
        print(f"\n📡 Making API request to v5alpha1...")
        req = urllib.request.Request(api_url)
        
        with urllib.request.urlopen(req, timeout=10) as response:
            content = response.read()
            status_code = response.status
            
            print(f"✓ Response Status: {status_code}")
            print(f"✓ Response Size: {len(content)} bytes")
            
            if not content or len(content) == 0:
                print("✓ Result: SAFE (empty response)")
                return True
            
            try:
                result = json.loads(content.decode('utf-8'))
                print(f"✓ Response JSON: {json.dumps(result, indent=2)}")
                
                if 'threat' in result or 'threats' in result:
                    print("⚠️  Result: THREAT DETECTED")
                    return True
                else:
                    print("✓ Result: SAFE")
                    return True
                    
            except json.JSONDecodeError:
                print(f"⚠️  Response is not JSON (might be protobuf)")
                print(f"   Raw content: {content[:200]}")
                return True
                
    except urllib.error.HTTPError as e:
        if e.code == 404:
            print(f"✓ Result: SAFE (404 - not in threat lists)")
            return True
        else:
            print(f"❌ HTTP Error: {e.code} - {e.reason}")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_v4_api(api_key, url, url_name):
    """Test Google Safe Browsing API v4 (fallback)"""
    print(f"\n{'='*60}")
    print(f"Testing v4 API: {url_name}")
    print(f"URL: {url}")
    print(f"{'='*60}")
    
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
        
        print(f"\n📡 Making API request to v4...")
        req = urllib.request.Request(
            api_url,
            data=json.dumps(payload).encode('utf-8'),
            headers={'Content-Type': 'application/json'}
        )
        
        with urllib.request.urlopen(req, timeout=10) as response:
            result = json.loads(response.read().decode('utf-8'))
            
            print(f"✓ Response: {json.dumps(result, indent=2)}")
            
            if 'matches' in result and result['matches']:
                print("⚠️  Result: THREAT DETECTED")
                for match in result['matches']:
                    print(f"   - Threat Type: {match.get('threatType')}")
                    print(f"   - Platform: {match.get('platformType')}")
                return True
            else:
                print("✓ Result: SAFE")
                return True
                
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_local_backend(url, url_name):
    """Test the local URLXpanda backend"""
    print(f"\n{'='*60}")
    print(f"Testing Local Backend: {url_name}")
    print(f"URL: {url}")
    print(f"{'='*60}")
    
    try:
        encoded_url = urllib.parse.quote(url, safe='')
        backend_url = f'http://localhost:8000/api/expand?url={encoded_url}'
        
        print(f"\n📡 Making request to local backend...")
        req = urllib.request.Request(backend_url)
        
        with urllib.request.urlopen(req, timeout=10) as response:
            result = json.loads(response.read().decode('utf-8'))
            
            print(f"✓ Response received")
            
            # Check safety info
            if 'metadata' in result and 'is_safe' in result['metadata']:
                safety = result['metadata']['is_safe']
                print(f"\n🛡️  Safety Analysis:")
                print(f"   - Safety Score: {safety.get('safety_score', 'N/A')}/100")
                print(f"   - Risk Level: {safety.get('risk_level', 'N/A')}")
                print(f"   - HTTPS: {safety.get('is_https', 'N/A')}")
                
                # Check Google Safe Browsing result
                gsb = safety.get('google_safe_browsing')
                if gsb:
                    print(f"\n🔍 Google Safe Browsing:")
                    print(f"   - Source: {gsb.get('source', 'N/A')}")
                    print(f"   - API Version: {gsb.get('api_version', 'N/A')}")
                    print(f"   - Is Safe: {gsb.get('is_safe', 'N/A')}")
                    if not gsb.get('is_safe'):
                        print(f"   - Threats: {gsb.get('threats', [])}")
                else:
                    print(f"\n⚠️  Google Safe Browsing: Not available (API key not set)")
                
                # Check warnings
                warnings = safety.get('warnings', [])
                if warnings:
                    print(f"\n⚠️  Warnings ({len(warnings)}):")
                    for warning in warnings:
                        print(f"   - [{warning.get('severity', 'unknown')}] {warning.get('message', 'N/A')}")
                        if 'source' in warning:
                            print(f"     Source: {warning['source']}")
                else:
                    print(f"\n✓ No warnings")
                
                return True
            else:
                print("⚠️  No safety information in response")
                return False
                
    except urllib.error.URLError as e:
        print(f"❌ Cannot connect to local backend: {e}")
        print(f"   Make sure the server is running: cd web && python3 serve.py")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main():
    print("="*60)
    print("Google Safe Browsing API Test Suite")
    print("="*60)
    
    # Check for API key
    api_key = os.environ.get('GOOGLE_SAFE_BROWSING_API_KEY')
    
    if not api_key:
        print("\n⚠️  WARNING: GOOGLE_SAFE_BROWSING_API_KEY not set!")
        print("   Set it with: export GOOGLE_SAFE_BROWSING_API_KEY='your-key'")
        print("\n   Skipping direct API tests...")
        print("   Will only test local backend (which may use pattern matching)")
        test_api = False
    else:
        print(f"\n✓ API Key found: {api_key[:10]}...{api_key[-4:]}")
        test_api = True
    
    results = {
        'v5_tests': [],
        'v4_tests': [],
        'backend_tests': []
    }
    
    # Test direct API calls (if key available)
    if test_api:
        print("\n" + "="*60)
        print("TESTING GOOGLE SAFE BROWSING API v5alpha1")
        print("="*60)
        
        for name, url in TEST_URLS.items():
            success = test_v5_api(api_key, url, name)
            results['v5_tests'].append((name, success))
        
        print("\n" + "="*60)
        print("TESTING GOOGLE SAFE BROWSING API v4 (Fallback)")
        print("="*60)
        
        # Test v4 with a couple URLs
        for name in ['malware', 'safe']:
            url = TEST_URLS[name]
            success = test_v4_api(api_key, url, name)
            results['v4_tests'].append((name, success))
    
    # Test local backend
    print("\n" + "="*60)
    print("TESTING LOCAL URLXPANDA BACKEND")
    print("="*60)
    
    for name, url in TEST_URLS.items():
        success = test_local_backend(url, name)
        results['backend_tests'].append((name, success))
    
    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    
    if test_api:
        v5_passed = sum(1 for _, success in results['v5_tests'] if success)
        v5_total = len(results['v5_tests'])
        print(f"\nv5alpha1 API Tests: {v5_passed}/{v5_total} passed")
        
        v4_passed = sum(1 for _, success in results['v4_tests'] if success)
        v4_total = len(results['v4_tests'])
        print(f"v4 API Tests: {v4_passed}/{v4_total} passed")
    
    backend_passed = sum(1 for _, success in results['backend_tests'] if success)
    backend_total = len(results['backend_tests'])
    print(f"Backend Tests: {backend_passed}/{backend_total} passed")
    
    print("\n" + "="*60)
    
    # Overall result
    all_passed = all(success for tests in results.values() for _, success in tests)
    if all_passed:
        print("✓ ALL TESTS PASSED!")
    else:
        print("⚠️  SOME TESTS FAILED")
        sys.exit(1)

if __name__ == '__main__':
    main()
