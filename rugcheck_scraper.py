"""
rugcheck.xyz Real Data Scraper
Phase 1 implementation - Tonight's first hour
"""

import requests
from bs4 import BeautifulSoup
import json
import asyncio
import time
from typing import Dict, Any, List

async def scrape_rugcheck_data(contract_address: str) -> Dict[str, Any]:
    """
    Scrape real data from rugcheck.xyz
    Returns actual liquidity, security flags, and risk indicators
    """
    
    print(f"🕷️ Starting rugcheck.xyz scrape for {contract_address}")
    start_time = time.time()
    
    try:
        # Phase 1: Direct HTTP request to rugcheck.xyz
        url = f"https://rugcheck.xyz/tokens/{contract_address}"
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36'
        }
        
        print(f"📡 Requesting: {url}")
        
        # Make request with timeout
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code != 200:
            print(f"❌ rugcheck.xyz returned status: {response.status_code}")
            return create_error_response("rugcheck_unavailable", response.status_code)
        
        # Parse HTML response
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Extract liquidity information
        liquidity_info = extract_liquidity_data(soup)
        
        # Extract security flags
        security_flags = extract_security_flags(soup)
        
        # Extract holder information (if available)
        holder_info = extract_holder_data(soup)
        
        # Extract market data
        market_info = extract_market_data(soup)
        
        elapsed_time = round(time.time() - start_time, 2)
        print(f"✅ rugcheck.xyz scrape completed in {elapsed_time}s")
        
        return {
            "success": True,
            "source": "rugcheck.xyz",
            "scrape_time": elapsed_time,
            "liquidity": liquidity_info,
            "security_flags": security_flags,
            "holder_data": holder_info,
            "market_data": market_info,
            "raw_available": True,
            "timestamp": time.time()
        }
        
    except requests.exceptions.Timeout:
        print("⏰ rugcheck.xyz request timed out")
        return create_error_response("timeout", "10s timeout exceeded")
        
    except requests.exceptions.RequestException as e:
        print(f"🌐 Network error accessing rugcheck.xyz: {e}")
        return create_error_response("network_error", str(e))
        
    except Exception as e:
        print(f"💥 Unexpected error in rugcheck scraping: {e}")
        return create_error_response("parsing_error", str(e))

def extract_liquidity_data(soup: BeautifulSoup) -> Dict[str, Any]:
    """
    Extract liquidity lock information from rugcheck.xyz HTML
    """
    liquidity_data = {
        "locked": None,
        "lock_duration": None,
        "liquidity_amount": None,
        "lock_percentage": None,
        "burn_percentage": None
    }
    
    try:
        # Look for liquidity lock indicators
        # rugcheck.xyz typically shows this in specific sections
        
        # Check for "LP Burned" or "LP Locked" text
        lock_elements = soup.find_all(text=lambda text: text and ('lock' in text.lower() or 'burn' in text.lower()))
        
        for element in lock_elements:
            parent = element.parent
            if parent:
                # Extract percentage if available
                if '%' in element:
                    import re
                    percentage_match = re.search(r'(\d+(?:\.\d+)?)%', element)
                    if percentage_match:
                        percentage = float(percentage_match.group(1))
                        
                        if 'burn' in element.lower():
                            liquidity_data["burn_percentage"] = percentage
                        elif 'lock' in element.lower():
                            liquidity_data["lock_percentage"] = percentage
                            liquidity_data["locked"] = True
                
                # Look for duration information
                if 'day' in element.lower() or 'month' in element.lower() or 'year' in element.lower():
                    liquidity_data["lock_duration"] = element.strip()
        
        # If we found lock percentage, mark as locked
        if liquidity_data["lock_percentage"] and liquidity_data["lock_percentage"] > 0:
            liquidity_data["locked"] = True
        elif liquidity_data["burn_percentage"] and liquidity_data["burn_percentage"] > 90:
            liquidity_data["locked"] = True  # Burned LP is effectively locked
            liquidity_data["lock_duration"] = "permanently burned"
        else:
            liquidity_data["locked"] = False
            
    except Exception as e:
        print(f"⚠️ Error extracting liquidity data: {e}")
        liquidity_data["error"] = str(e)
    
    return liquidity_data

def extract_security_flags(soup: BeautifulSoup) -> List[str]:
    """
    Extract security flags and warnings from rugcheck.xyz
    """
    security_flags = []
    
    try:
        # Look for common rugcheck.xyz security indicators
        warning_indicators = [
            "mint authority",
            "freeze authority", 
            "honeypot",
            "suspicious",
            "high risk",
            "medium risk",
            "low risk",
            "verified",
            "renounced"
        ]
        
        for indicator in warning_indicators:
            elements = soup.find_all(text=lambda text: text and indicator.lower() in text.lower())
            
            for element in elements:
                # Clean up and format security flag
                flag_text = element.strip()
                if len(flag_text) < 100:  # Avoid very long text snippets
                    
                    # Add appropriate emoji based on content
                    if any(word in flag_text.lower() for word in ['verified', 'renounced', 'locked', 'burned']):
                        security_flags.append(f"✅ {flag_text}")
                    elif any(word in flag_text.lower() for word in ['suspicious', 'high risk', 'honeypot']):
                        security_flags.append(f"🚨 {flag_text}")
                    elif 'medium risk' in flag_text.lower():
                        security_flags.append(f"⚠️ {flag_text}")
                    else:
                        security_flags.append(f"ℹ️ {flag_text}")
        
        # Remove duplicates while preserving order
        security_flags = list(dict.fromkeys(security_flags))
        
        # Limit to most important flags
        security_flags = security_flags[:8]
        
    except Exception as e:
        print(f"⚠️ Error extracting security flags: {e}")
        security_flags.append(f"⚠️ Error parsing security data: {str(e)}")
    
    return security_flags if security_flags else ["ℹ️ Security analysis completed"]

def extract_holder_data(soup: BeautifulSoup) -> Dict[str, Any]:
    """
    Extract holder distribution data from rugcheck.xyz
    """
    holder_data = {
        "total_holders": None,
        "top_holder_percent": None,
        "top_10_percent": None,
        "distribution_score": None
    }
    
    try:
        # rugcheck.xyz might show holder concentration data
        # Look for percentage patterns
        import re
        
        text_content = soup.get_text()
        
        # Look for patterns like "Top holder: 15.5%"
        holder_patterns = [
            r'top holder[:\s]+(\d+(?:\.\d+)?)%',
            r'largest holder[:\s]+(\d+(?:\.\d+)?)%',
            r'concentration[:\s]+(\d+(?:\.\d+)?)%'
        ]
        
        for pattern in holder_patterns:
            match = re.search(pattern, text_content, re.IGNORECASE)
            if match:
                holder_data["top_holder_percent"] = float(match.group(1))
                break
        
        # Look for total holder count
        holder_count_pattern = r'(\d+)\s+holders?'
        holder_count_match = re.search(holder_count_pattern, text_content, re.IGNORECASE)
        if holder_count_match:
            holder_data["total_holders"] = int(holder_count_match.group(1))
        
        # Assign distribution score based on top holder percentage
        if holder_data["top_holder_percent"]:
            top_percent = holder_data["top_holder_percent"]
            if top_percent > 50:
                holder_data["distribution_score"] = "Very Poor"
            elif top_percent > 30:
                holder_data["distribution_score"] = "Poor"
            elif top_percent > 20:
                holder_data["distribution_score"] = "Fair"
            elif top_percent > 10:
                holder_data["distribution_score"] = "Good"
            else:
                holder_data["distribution_score"] = "Excellent"
        
    except Exception as e:
        print(f"⚠️ Error extracting holder data: {e}")
        holder_data["error"] = str(e)
    
    return holder_data

def extract_market_data(soup: BeautifulSoup) -> Dict[str, Any]:
    """
    Extract available market data from rugcheck.xyz
    """
    market_data = {
        "market_cap": None,
        "age_info": None,
        "creation_date": None
    }
    
    try:
        # rugcheck.xyz might show basic market information
        text_content = soup.get_text()
        
        import re
        
        # Look for market cap patterns
        mcap_patterns = [
            r'market cap[:\s]+\$?([\d,]+)',
            r'mcap[:\s]+\$?([\d,]+)'
        ]
        
        for pattern in mcap_patterns:
            match = re.search(pattern, text_content, re.IGNORECASE)
            if match:
                mcap_str = match.group(1).replace(',', '')
                market_data["market_cap"] = f"${mcap_str}"
                break
        
        # Look for age/creation information
        age_patterns = [
            r'created\s+(\d+)\s+(day|hour|month)s?\s+ago',
            r'age[:\s]+(\d+)\s+(day|hour|month)s?'
        ]
        
        for pattern in age_patterns:
            match = re.search(pattern, text_content, re.IGNORECASE)
            if match:
                amount = int(match.group(1))
                unit = match.group(2).lower()
                market_data["age_info"] = f"{amount} {unit}{'s' if amount > 1 else ''} ago"
                break
        
    except Exception as e:
        print(f"⚠️ Error extracting market data: {e}")
        market_data["error"] = str(e)
    
    return market_data

def create_error_response(error_type: str, error_details: Any) -> Dict[str, Any]:
    """Create standardized error response"""
    return {
        "success": False,
        "error_type": error_type,
        "error_details": error_details,
        "liquidity": {"locked": None, "error": "Data unavailable"},
        "security_flags": [f"⚠️ Unable to fetch rugcheck data: {error_type}"],
        "holder_data": {"error": "Data unavailable"},
        "market_data": {"error": "Data unavailable"},
        "timestamp": time.time()
    }

# Test function for development
async def test_rugcheck_scraper():
    """Test the rugcheck scraper with a known token"""
    
    # Test with USDC (should be very safe)
    usdc_address = "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v"
    
    print("🧪 Testing rugcheck scraper...")
    result = await scrape_rugcheck_data(usdc_address)
    
    print("📊 Test Results:")
    print(json.dumps(result, indent=2))
    
    return result

if __name__ == "__main__":
    # Run test
    asyncio.run(test_rugcheck_scraper())