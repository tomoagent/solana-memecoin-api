"""
Explore rugcheck.xyz API endpoints
Find the correct API structure for token analysis
"""

import requests
import json

def explore_rugcheck_api():
    """
    Explore rugcheck.xyz API to find correct endpoints
    """
    
    bonk_address = "DezXAZ8z7PnrnRJjz3wXBoRgixCa6xjnB7YaB1pPB263"
    
    # Common API endpoint patterns to try
    endpoints_to_try = [
        f"https://api.rugcheck.xyz/v1/tokens/{bonk_address}",
        f"https://api.rugcheck.xyz/api/v1/tokens/{bonk_address}",
        f"https://api.rugcheck.xyz/tokens/{bonk_address}",
        f"https://api.rugcheck.xyz/token/{bonk_address}",
        f"https://api.rugcheck.xyz/check/{bonk_address}",
        f"https://api.rugcheck.xyz/analyze/{bonk_address}",
        f"https://api.rugcheck.xyz/v1/analyze/{bonk_address}",
        f"https://api.rugcheck.xyz/api/tokens/{bonk_address}",
        "https://api.rugcheck.xyz/",
        "https://api.rugcheck.xyz/health",
        "https://api.rugcheck.xyz/v1/",
        "https://api.rugcheck.xyz/api/v1/"
    ]
    
    print("🔍 Exploring rugcheck.xyz API endpoints...")
    
    headers = {
        'User-Agent': 'Solana-Memecoin-Analyzer/3.0',
        'Accept': 'application/json',
        'Content-Type': 'application/json'
    }
    
    successful_endpoints = []
    
    for endpoint in endpoints_to_try:
        try:
            print(f"\n🌐 Trying: {endpoint}")
            
            response = requests.get(endpoint, headers=headers, timeout=10)
            
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                print(f"   ✅ SUCCESS!")
                
                try:
                    data = response.json()
                    print(f"   📄 Response type: JSON")
                    print(f"   📊 Keys: {list(data.keys()) if isinstance(data, dict) else 'Not a dict'}")
                    
                    # Save successful response
                    with open(f'rugcheck_api_success_{len(successful_endpoints)}.json', 'w') as f:
                        json.dump(data, f, indent=2)
                    
                    successful_endpoints.append({
                        'endpoint': endpoint,
                        'status': response.status_code,
                        'data_keys': list(data.keys()) if isinstance(data, dict) else None,
                        'response_sample': str(data)[:200]
                    })
                    
                except json.JSONDecodeError:
                    print(f"   📄 Response type: Text/HTML")
                    print(f"   📝 Content preview: {response.text[:200]}...")
                    
                    # Save text response
                    with open(f'rugcheck_api_response_{len(successful_endpoints)}.txt', 'w') as f:
                        f.write(response.text)
                    
                    successful_endpoints.append({
                        'endpoint': endpoint,
                        'status': response.status_code,
                        'content_type': response.headers.get('content-type', 'unknown'),
                        'content_preview': response.text[:200]
                    })
                    
            elif response.status_code in [404, 405]:
                print(f"   ❌ Not found")
            elif response.status_code == 403:
                print(f"   🔒 Forbidden")
            elif response.status_code == 429:
                print(f"   ⏰ Rate limited")
            else:
                print(f"   ⚠️  Other error")
                print(f"   📝 Response: {response.text[:100]}...")
                
        except requests.exceptions.Timeout:
            print(f"   ⏰ Timeout")
        except requests.exceptions.RequestException as e:
            print(f"   💥 Request error: {str(e)}")
        except Exception as e:
            print(f"   💥 Unexpected error: {str(e)}")
    
    print(f"\n📊 EXPLORATION SUMMARY:")
    print(f"Tried {len(endpoints_to_try)} endpoints")
    print(f"Found {len(successful_endpoints)} successful responses")
    
    if successful_endpoints:
        print(f"\n✅ SUCCESSFUL ENDPOINTS:")
        for i, endpoint_info in enumerate(successful_endpoints):
            print(f"  {i+1}. {endpoint_info['endpoint']}")
            print(f"     Status: {endpoint_info['status']}")
            if 'data_keys' in endpoint_info:
                print(f"     Keys: {endpoint_info['data_keys']}")
            print()
    else:
        print(f"\n❌ No successful endpoints found")
        print(f"rugcheck.xyz API may require authentication or have different structure")
    
    return successful_endpoints

if __name__ == "__main__":
    explore_rugcheck_api()