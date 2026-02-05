"""
Advanced rugcheck.xyz Data Scraper
Phase 4 implementation - Maximum 4 hours completion
Playwright-powered JavaScript rendering + intelligent fallbacks
"""

import asyncio
import time
import json
import re
from typing import Dict, Any, List, Optional
from playwright.async_api import async_playwright, Page, Browser, TimeoutError as PlaywrightTimeoutError
import requests
from bs4 import BeautifulSoup

class AdvancedRugcheckScraper:
    """
    Advanced rugcheck.xyz scraper with multiple data extraction strategies:
    1. Playwright (JavaScript rendering) - Primary method
    2. Direct HTTP + BeautifulSoup - Fallback method  
    3. Intelligent data parsing and validation
    """
    
    def __init__(self):
        self.playwright_timeout = 15000  # 15 seconds
        self.http_timeout = 10  # 10 seconds
        self.browser = None
        self.page = None
        
        # Data patterns for intelligent extraction
        self.patterns = {
            "liquidity_lock": {
                "selectors": [
                    "[data-testid='liquidity-lock']",
                    ".liquidity-lock",
                    ".lp-lock",
                    "*:contains('LP Locked')",
                    "*:contains('Liquidity Lock')"
                ],
                "text_patterns": [
                    r'LP.*?(?:locked|burned).*?(\d+(?:\.\d+)?)%',
                    r'liquidity.*?(?:locked|burned).*?(\d+(?:\.\d+)?)%',
                    r'(\d+(?:\.\d+)?)%.*?(?:locked|burned)',
                    r'Lock.*?(\d+)\s*(day|month|year)s?',
                    r'Burn.*?(\d+(?:\.\d+)?)%'
                ]
            },
            "holder_concentration": {
                "selectors": [
                    "[data-testid='top-holders']",
                    ".holder-distribution",
                    ".top-holders",
                    "*:contains('Top Holder')",
                    "*:contains('largest holder')"
                ],
                "text_patterns": [
                    r'top holder[:\s]*(\d+(?:\.\d+)?)%',
                    r'largest holder[:\s]*(\d+(?:\.\d+)?)%',
                    r'concentration[:\s]*(\d+(?:\.\d+)?)%',
                    r'(\d+(?:\.\d+)?)%\s*(?:top|largest)',
                    r'holder.*?(\d+(?:\.\d+)?)%'
                ]
            },
            "security_flags": {
                "selectors": [
                    "[data-testid='security-flags']",
                    ".security-warnings",
                    ".risk-flags",
                    ".warnings",
                    "*:contains('Authority')",
                    "*:contains('Risk')"
                ],
                "keywords": [
                    "mint authority", "freeze authority", "honeypot", 
                    "high risk", "medium risk", "low risk",
                    "verified", "renounced", "suspicious",
                    "locked", "burned", "safe"
                ]
            },
            "market_data": {
                "selectors": [
                    "[data-testid='market-cap']",
                    ".market-cap",
                    ".mcap",
                    "*:contains('Market Cap')",
                    "*:contains('Age')"
                ],
                "text_patterns": [
                    r'market cap[:\s]*\$?([\d,]+(?:\.\d+)?[kmb]?)',
                    r'mcap[:\s]*\$?([\d,]+(?:\.\d+)?[kmb]?)',
                    r'age[:\s]*(\d+)\s*(hour|day|month|year)s?',
                    r'created[:\s]*(\d+)\s*(hour|day|month|year)s?\s*ago'
                ]
            }
        }
    
    async def scrape_rugcheck_data(self, contract_address: str) -> Dict[str, Any]:
        """
        Main entry point - attempts Playwright first, then falls back to HTTP
        """
        
        print(f"🚀 Starting ADVANCED rugcheck.xyz scrape for {contract_address}")
        start_time = time.time()
        
        try:
            # Attempt 1: Playwright (JavaScript rendering)
            playwright_result = await self._scrape_with_playwright(contract_address)
            
            if playwright_result["success"] and self._has_meaningful_data(playwright_result):
                elapsed_time = round(time.time() - start_time, 2)
                playwright_result["total_scrape_time"] = elapsed_time
                playwright_result["method_used"] = "playwright_primary"
                print(f"✅ PLAYWRIGHT SUCCESS: Advanced scrape completed in {elapsed_time}s")
                return playwright_result
            
            print("⚠️ Playwright data insufficient, trying HTTP fallback...")
            
            # Attempt 2: HTTP + BeautifulSoup fallback
            http_result = await self._scrape_with_http(contract_address)
            
            # Merge best data from both attempts
            combined_result = self._merge_data_sources(playwright_result, http_result)
            
            elapsed_time = round(time.time() - start_time, 2)
            combined_result["total_scrape_time"] = elapsed_time
            combined_result["method_used"] = "playwright_http_combined"
            
            print(f"✅ COMBINED SUCCESS: Advanced scrape completed in {elapsed_time}s")
            return combined_result
            
        except Exception as e:
            print(f"💥 ADVANCED SCRAPE FAILED: {e}")
            
            # Final fallback to basic HTTP
            try:
                http_result = await self._scrape_with_http(contract_address)
                elapsed_time = round(time.time() - start_time, 2)
                http_result["total_scrape_time"] = elapsed_time
                http_result["method_used"] = "http_fallback_only"
                return http_result
            except:
                return self._create_error_response("all_methods_failed", str(e))
    
    async def _scrape_with_playwright(self, contract_address: str) -> Dict[str, Any]:
        """
        Primary method: Use Playwright for JavaScript-rendered content
        """
        
        print(f"🎭 Playwright scraping: {contract_address}")
        
        try:
            async with async_playwright() as p:
                browser = await p.chromium.launch(
                    headless=True,
                    args=['--no-sandbox', '--disable-dev-shm-usage']
                )
                page = await browser.new_page()
                
                # Set realistic user agent
                await page.set_extra_http_headers({
                    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36'
                })
                
                url = f"https://rugcheck.xyz/tokens/{contract_address}"
                print(f"🌐 Loading: {url}")
                
                # Navigate and wait for dynamic content
                await page.goto(url, wait_until='networkidle', timeout=self.playwright_timeout)
                
                # Wait for potential dynamic content loading
                await page.wait_for_timeout(3000)  # 3 second wait for JS to execute
                
                # Extract data using multiple strategies
                liquidity_data = await self._extract_liquidity_playwright(page)
                holder_data = await self._extract_holder_data_playwright(page)
                security_flags = await self._extract_security_flags_playwright(page)
                market_data = await self._extract_market_data_playwright(page)
                
                await browser.close()
                
                return {
                    "success": True,
                    "source": "rugcheck.xyz",
                    "method": "playwright",
                    "liquidity": liquidity_data,
                    "holder_data": holder_data,
                    "security_flags": security_flags,
                    "market_data": market_data,
                    "timestamp": time.time()
                }
                
        except PlaywrightTimeoutError:
            print("⏰ Playwright timeout - page took too long to load")
            return self._create_error_response("playwright_timeout", "Page load timeout")
            
        except Exception as e:
            print(f"💥 Playwright error: {e}")
            return self._create_error_response("playwright_error", str(e))
    
    async def _scrape_with_http(self, contract_address: str) -> Dict[str, Any]:
        """
        Fallback method: Direct HTTP request + BeautifulSoup
        """
        
        print(f"🌐 HTTP fallback scraping: {contract_address}")
        
        try:
            url = f"https://rugcheck.xyz/tokens/{contract_address}"
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Accept-Encoding': 'gzip, deflate',
                'Connection': 'keep-alive'
            }
            
            response = requests.get(url, headers=headers, timeout=self.http_timeout)
            
            if response.status_code != 200:
                return self._create_error_response("http_error", f"Status {response.status_code}")
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extract using pattern-based parsing
            liquidity_data = self._extract_liquidity_http(soup)
            holder_data = self._extract_holder_data_http(soup)
            security_flags = self._extract_security_flags_http(soup)
            market_data = self._extract_market_data_http(soup)
            
            return {
                "success": True,
                "source": "rugcheck.xyz",
                "method": "http",
                "liquidity": liquidity_data,
                "holder_data": holder_data,
                "security_flags": security_flags,
                "market_data": market_data,
                "timestamp": time.time()
            }
            
        except Exception as e:
            print(f"💥 HTTP scraping error: {e}")
            return self._create_error_response("http_error", str(e))
    
    async def _extract_liquidity_playwright(self, page: Page) -> Dict[str, Any]:
        """
        Extract liquidity data using Playwright selectors and text parsing
        """
        
        liquidity_data = {
            "locked": None,
            "lock_percentage": None,
            "burn_percentage": None,
            "lock_duration": None,
            "confidence": 0
        }
        
        try:
            # Get page content
            content = await page.content()
            
            # Try CSS selectors first
            for selector in self.patterns["liquidity_lock"]["selectors"]:
                try:
                    elements = await page.query_selector_all(selector)
                    for element in elements:
                        text = await element.text_content()
                        if text and ('lock' in text.lower() or 'burn' in text.lower()):
                            # Parse the text for percentages and durations
                            parsed_data = self._parse_liquidity_text(text)
                            if parsed_data:
                                liquidity_data.update(parsed_data)
                                liquidity_data["confidence"] += 0.3
                except:
                    continue
            
            # Try text pattern matching on full page content
            for pattern in self.patterns["liquidity_lock"]["text_patterns"]:
                matches = re.finditer(pattern, content, re.IGNORECASE)
                for match in matches:
                    percentage = float(match.group(1))
                    
                    if 'lock' in match.group(0).lower():
                        liquidity_data["lock_percentage"] = percentage
                        liquidity_data["locked"] = True
                        liquidity_data["confidence"] += 0.4
                    elif 'burn' in match.group(0).lower():
                        liquidity_data["burn_percentage"] = percentage
                        if percentage > 90:
                            liquidity_data["locked"] = True
                        liquidity_data["confidence"] += 0.4
            
            # Final determination
            if liquidity_data["locked"] is None:
                if liquidity_data["lock_percentage"] or liquidity_data["burn_percentage"]:
                    liquidity_data["locked"] = True
                else:
                    liquidity_data["locked"] = False
                    
        except Exception as e:
            print(f"⚠️ Playwright liquidity extraction error: {e}")
            liquidity_data["error"] = str(e)
        
        return liquidity_data
    
    async def _extract_holder_data_playwright(self, page: Page) -> Dict[str, Any]:
        """
        Extract holder concentration data using Playwright
        """
        
        holder_data = {
            "top_holder_percent": None,
            "total_holders": None,
            "distribution_score": None,
            "confidence": 0
        }
        
        try:
            content = await page.content()
            
            # Look for holder concentration patterns
            for pattern in self.patterns["holder_concentration"]["text_patterns"]:
                match = re.search(pattern, content, re.IGNORECASE)
                if match:
                    percentage = float(match.group(1))
                    holder_data["top_holder_percent"] = percentage
                    holder_data["confidence"] += 0.4
                    
                    # Assign distribution score
                    if percentage > 50:
                        holder_data["distribution_score"] = "Very Poor"
                    elif percentage > 30:
                        holder_data["distribution_score"] = "Poor"
                    elif percentage > 20:
                        holder_data["distribution_score"] = "Fair"
                    elif percentage > 10:
                        holder_data["distribution_score"] = "Good"
                    else:
                        holder_data["distribution_score"] = "Excellent"
                    break
            
            # Look for total holder count
            holder_count_pattern = r'(\d+)\s+holders?'
            match = re.search(holder_count_pattern, content, re.IGNORECASE)
            if match:
                holder_data["total_holders"] = int(match.group(1))
                holder_data["confidence"] += 0.2
                
        except Exception as e:
            print(f"⚠️ Playwright holder data extraction error: {e}")
            holder_data["error"] = str(e)
        
        return holder_data
    
    async def _extract_security_flags_playwright(self, page: Page) -> List[str]:
        """
        Extract security flags using Playwright
        """
        
        security_flags = []
        
        try:
            content = await page.content()
            
            # Look for security-related keywords
            for keyword in self.patterns["security_flags"]["keywords"]:
                if keyword.lower() in content.lower():
                    # Find surrounding context
                    pattern = f'.{{0,50}}{re.escape(keyword)}.{{0,50}}'
                    matches = re.finditer(pattern, content, re.IGNORECASE)
                    
                    for match in matches:
                        context = match.group(0).strip()
                        
                        # Add appropriate emoji
                        if any(word in context.lower() for word in ['verified', 'renounced', 'locked', 'burned', 'safe']):
                            security_flags.append(f"✅ {context}")
                        elif any(word in context.lower() for word in ['high risk', 'honeypot', 'suspicious']):
                            security_flags.append(f"🚨 {context}")
                        elif 'medium risk' in context.lower():
                            security_flags.append(f"⚠️ {context}")
                        else:
                            security_flags.append(f"ℹ️ {context}")
                        
                        if len(security_flags) >= 8:  # Limit flags
                            break
            
            # Remove duplicates while preserving order
            security_flags = list(dict.fromkeys(security_flags))
            
        except Exception as e:
            print(f"⚠️ Playwright security flags extraction error: {e}")
            security_flags.append(f"⚠️ Error extracting security data: {str(e)}")
        
        return security_flags if security_flags else ["ℹ️ Security analysis completed"]
    
    async def _extract_market_data_playwright(self, page: Page) -> Dict[str, Any]:
        """
        Extract market data using Playwright
        """
        
        market_data = {
            "market_cap": None,
            "age_info": None,
            "creation_date": None,
            "confidence": 0
        }
        
        try:
            content = await page.content()
            
            # Market cap patterns
            for pattern in self.patterns["market_data"]["text_patterns"]:
                match = re.search(pattern, content, re.IGNORECASE)
                if match:
                    if 'market cap' in pattern or 'mcap' in pattern:
                        market_data["market_cap"] = f"${match.group(1)}"
                        market_data["confidence"] += 0.3
                    elif 'age' in pattern or 'created' in pattern:
                        amount = match.group(1)
                        unit = match.group(2)
                        market_data["age_info"] = f"{amount} {unit}{'s' if int(amount) > 1 else ''} ago"
                        market_data["confidence"] += 0.4
                        
        except Exception as e:
            print(f"⚠️ Playwright market data extraction error: {e}")
            market_data["error"] = str(e)
        
        return market_data
    
    def _extract_liquidity_http(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """
        HTTP fallback liquidity extraction
        """
        
        liquidity_data = {
            "locked": False,
            "lock_percentage": None,
            "burn_percentage": None,
            "lock_duration": None,
            "confidence": 0.2  # Lower confidence for HTTP method
        }
        
        try:
            # Simple text-based parsing
            text_content = soup.get_text()
            
            for pattern in self.patterns["liquidity_lock"]["text_patterns"]:
                match = re.search(pattern, text_content, re.IGNORECASE)
                if match:
                    percentage = float(match.group(1))
                    
                    if 'lock' in match.group(0).lower():
                        liquidity_data["lock_percentage"] = percentage
                        liquidity_data["locked"] = True
                        liquidity_data["confidence"] += 0.3
                    elif 'burn' in match.group(0).lower():
                        liquidity_data["burn_percentage"] = percentage
                        if percentage > 90:
                            liquidity_data["locked"] = True
                        liquidity_data["confidence"] += 0.3
                    break
                        
        except Exception as e:
            liquidity_data["error"] = str(e)
        
        return liquidity_data
    
    def _extract_holder_data_http(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """HTTP fallback holder data extraction"""
        
        holder_data = {
            "top_holder_percent": None,
            "total_holders": None,
            "distribution_score": None,
            "confidence": 0.2
        }
        
        try:
            text_content = soup.get_text()
            
            for pattern in self.patterns["holder_concentration"]["text_patterns"]:
                match = re.search(pattern, text_content, re.IGNORECASE)
                if match:
                    holder_data["top_holder_percent"] = float(match.group(1))
                    holder_data["confidence"] += 0.3
                    break
                    
        except Exception as e:
            holder_data["error"] = str(e)
        
        return holder_data
    
    def _extract_security_flags_http(self, soup: BeautifulSoup) -> List[str]:
        """HTTP fallback security flags extraction"""
        
        security_flags = []
        
        try:
            text_content = soup.get_text()
            
            for keyword in self.patterns["security_flags"]["keywords"][:5]:  # Limited search
                if keyword.lower() in text_content.lower():
                    security_flags.append(f"ℹ️ {keyword.title()} mentioned")
                    
        except Exception as e:
            security_flags.append(f"⚠️ Error: {str(e)}")
        
        return security_flags if security_flags else ["ℹ️ Basic security scan completed"]
    
    def _extract_market_data_http(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """HTTP fallback market data extraction"""
        
        market_data = {
            "market_cap": None,
            "age_info": None,
            "creation_date": None,
            "confidence": 0.2
        }
        
        try:
            text_content = soup.get_text()
            
            # Basic pattern matching
            mcap_match = re.search(r'market cap[:\s]*\$?([\d,]+)', text_content, re.IGNORECASE)
            if mcap_match:
                market_data["market_cap"] = f"${mcap_match.group(1)}"
                market_data["confidence"] += 0.3
                
        except Exception as e:
            market_data["error"] = str(e)
        
        return market_data
    
    def _parse_liquidity_text(self, text: str) -> Optional[Dict[str, Any]]:
        """Parse liquidity information from text"""
        
        try:
            parsed = {}
            
            # Look for percentages
            percentage_match = re.search(r'(\d+(?:\.\d+)?)%', text)
            if percentage_match:
                percentage = float(percentage_match.group(1))
                
                if 'lock' in text.lower():
                    parsed["lock_percentage"] = percentage
                    parsed["locked"] = True
                elif 'burn' in text.lower():
                    parsed["burn_percentage"] = percentage
                    if percentage > 90:
                        parsed["locked"] = True
            
            # Look for duration
            duration_match = re.search(r'(\d+)\s*(day|month|year)s?', text, re.IGNORECASE)
            if duration_match:
                parsed["lock_duration"] = f"{duration_match.group(1)} {duration_match.group(2)}{'s' if int(duration_match.group(1)) > 1 else ''}"
            
            return parsed if parsed else None
            
        except:
            return None
    
    def _has_meaningful_data(self, result: Dict[str, Any]) -> bool:
        """
        Check if the scraped data contains meaningful information
        """
        
        if not result.get("success"):
            return False
        
        # Check if we got meaningful liquidity data
        liquidity = result.get("liquidity", {})
        if liquidity.get("locked") is not None or liquidity.get("lock_percentage") is not None:
            return True
        
        # Check if we got meaningful holder data
        holder_data = result.get("holder_data", {})
        if holder_data.get("top_holder_percent") is not None:
            return True
        
        # Check if we got meaningful security flags
        security_flags = result.get("security_flags", [])
        if len(security_flags) > 1:  # More than just the default message
            return True
        
        # Check confidence levels
        total_confidence = 0
        confidence_count = 0
        
        for data_dict in [liquidity, holder_data, result.get("market_data", {})]:
            if isinstance(data_dict, dict) and "confidence" in data_dict:
                total_confidence += data_dict["confidence"]
                confidence_count += 1
        
        avg_confidence = total_confidence / confidence_count if confidence_count > 0 else 0
        
        return avg_confidence > 0.3  # At least 30% confidence threshold
    
    def _merge_data_sources(self, playwright_result: Dict[str, Any], http_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Intelligently merge data from both sources, prioritizing higher confidence data
        """
        
        if not playwright_result.get("success"):
            return http_result
        
        if not http_result.get("success"):
            return playwright_result
        
        merged = {
            "success": True,
            "source": "rugcheck.xyz",
            "method": "merged_playwright_http",
            "timestamp": time.time()
        }
        
        # Merge liquidity data (choose higher confidence)
        pw_liquidity = playwright_result.get("liquidity", {})
        http_liquidity = http_result.get("liquidity", {})
        
        pw_confidence = pw_liquidity.get("confidence", 0)
        http_confidence = http_liquidity.get("confidence", 0)
        
        if pw_confidence >= http_confidence:
            merged["liquidity"] = pw_liquidity
        else:
            merged["liquidity"] = http_liquidity
        
        # Merge holder data (same logic)
        pw_holder = playwright_result.get("holder_data", {})
        http_holder = http_result.get("holder_data", {})
        
        pw_h_confidence = pw_holder.get("confidence", 0)
        http_h_confidence = http_holder.get("confidence", 0)
        
        if pw_h_confidence >= http_h_confidence:
            merged["holder_data"] = pw_holder
        else:
            merged["holder_data"] = http_holder
        
        # Merge security flags (combine both sources)
        pw_flags = playwright_result.get("security_flags", [])
        http_flags = http_result.get("security_flags", [])
        
        all_flags = pw_flags + http_flags
        merged["security_flags"] = list(dict.fromkeys(all_flags))[:8]  # Remove duplicates, limit to 8
        
        # Merge market data (higher confidence wins)
        pw_market = playwright_result.get("market_data", {})
        http_market = http_result.get("market_data", {})
        
        pw_m_confidence = pw_market.get("confidence", 0)
        http_m_confidence = http_market.get("confidence", 0)
        
        if pw_m_confidence >= http_m_confidence:
            merged["market_data"] = pw_market
        else:
            merged["market_data"] = http_market
        
        return merged
    
    def _create_error_response(self, error_type: str, error_details: str) -> Dict[str, Any]:
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

# Updated main scraping function for backward compatibility
async def scrape_rugcheck_data(contract_address: str) -> Dict[str, Any]:
    """
    Main entry point for rugcheck scraping - uses advanced scraper
    """
    
    scraper = AdvancedRugcheckScraper()
    return await scraper.scrape_rugcheck_data(contract_address)

# Test function
async def test_advanced_rugcheck():
    """
    Test the advanced rugcheck scraper
    """
    
    test_tokens = [
        ("BONK", "DezXAZ8z7PnrnRJjz3wXBoRgixCa6xjnB7YaB1pPB263"),
        ("USDC", "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v")
    ]
    
    scraper = AdvancedRugcheckScraper()
    
    for name, address in test_tokens:
        print(f"\n🧪 Testing ADVANCED scraper with {name}...")
        
        result = await scraper.scrape_rugcheck_data(address)
        
        print(f"Method used: {result.get('method_used', 'unknown')}")
        print(f"Success: {result['success']}")
        print(f"Time: {result.get('total_scrape_time', 'N/A')}s")
        
        if result["success"]:
            liquidity = result.get("liquidity", {})
            print(f"Liquidity locked: {liquidity.get('locked')}")
            print(f"Confidence: {liquidity.get('confidence', 0)}")
            
            holder_data = result.get("holder_data", {})
            print(f"Top holder: {holder_data.get('top_holder_percent')}%")
            
            flags = result.get("security_flags", [])
            print(f"Security flags: {len(flags)}")
            for flag in flags[:3]:
                print(f"  {flag}")
        else:
            print(f"Error: {result.get('error_type')} - {result.get('error_details')}")

if __name__ == "__main__":
    asyncio.run(test_advanced_rugcheck())