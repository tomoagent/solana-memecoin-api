"""
Debug rugcheck.xyz page structure
Understand what selectors and data patterns actually work
"""

import asyncio
from playwright.async_api import async_playwright
import re

async def debug_rugcheck_structure():
    """
    Debug rugcheck.xyz to understand its actual HTML structure
    """
    
    contract_address = "DezXAZ8z7PnrnRJjz3wXBoRgixCa6xjnB7YaB1pPB263"  # BONK
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)  # Headless mode
        page = await browser.new_page()
        
        url = f"https://rugcheck.xyz/tokens/{contract_address}"
        print(f"🔍 Debugging: {url}")
        
        # Navigate to page
        await page.goto(url, wait_until='networkidle', timeout=30000)
        await page.wait_for_timeout(5000)  # Wait 5s for JS to execute
        
        # Get page title for verification
        title = await page.title()
        print(f"📄 Page title: {title}")
        
        # Get all text content
        full_text = await page.text_content('body')
        print(f"\n📝 Full page text (first 500 chars):")
        print(full_text[:500])
        
        # Save full HTML for inspection
        html_content = await page.content()
        with open('rugcheck_debug.html', 'w') as f:
            f.write(html_content)
        print(f"\n💾 Full HTML saved to rugcheck_debug.html")
        
        # Look for specific patterns in text
        liquidity_patterns = [
            r'liquidity.*?lock',
            r'lp.*?lock',
            r'lock.*?%',
            r'burn.*?%',
            r'\d+%.*?lock',
            r'\d+%.*?burn'
        ]
        
        print(f"\n🔍 Searching for liquidity patterns:")
        for pattern in liquidity_patterns:
            matches = re.finditer(pattern, full_text, re.IGNORECASE)
            for match in matches:
                start = max(0, match.start() - 50)
                end = min(len(full_text), match.end() + 50)
                context = full_text[start:end]
                print(f"  Pattern '{pattern}': ...{context}...")
        
        # Look for holder patterns
        holder_patterns = [
            r'top.*?holder.*?\d+%',
            r'\d+%.*?holder',
            r'holder.*?\d+%',
            r'concentration.*?\d+%'
        ]
        
        print(f"\n👥 Searching for holder patterns:")
        for pattern in holder_patterns:
            matches = re.finditer(pattern, full_text, re.IGNORECASE)
            for match in matches:
                start = max(0, match.start() - 50)
                end = min(len(full_text), match.end() + 50)
                context = full_text[start:end]
                print(f"  Pattern '{pattern}': ...{context}...")
        
        # Try to find common HTML elements that might contain data
        selectors_to_try = [
            'div',
            'span',
            'p',
            '[class*="lock"]',
            '[class*="liquidity"]',
            '[class*="holder"]',
            '[class*="burn"]',
            '[data-testid]'
        ]
        
        print(f"\n🎯 Checking common selectors:")
        for selector in selectors_to_try:
            try:
                elements = await page.query_selector_all(selector)
                if len(elements) > 0:
                    print(f"  {selector}: {len(elements)} elements found")
                    
                    # Sample first few elements
                    for i, element in enumerate(elements[:3]):
                        text = await element.text_content()
                        if text and len(text.strip()) > 0:
                            print(f"    Element {i}: {text[:100]}...")
            except Exception as e:
                print(f"    {selector}: Error - {e}")
        
        # Check for specific data attributes
        data_attributes = [
            'data-testid',
            'data-cy',
            'data-qa',
            'id',
            'class'
        ]
        
        print(f"\n🏷️ Checking data attributes:")
        try:
            all_elements = await page.query_selector_all('*[data-testid], *[id], *[class]')
            attribute_info = []
            
            for element in all_elements[:20]:  # Sample first 20
                attrs = await element.evaluate('el => el.attributes')
                element_info = {}
                
                for attr_name in data_attributes:
                    try:
                        attr_value = await element.get_attribute(attr_name)
                        if attr_value:
                            element_info[attr_name] = attr_value
                    except:
                        pass
                
                if element_info:
                    text = await element.text_content()
                    if text and len(text.strip()) > 5:
                        element_info['text_sample'] = text[:50]
                        attribute_info.append(element_info)
            
            for info in attribute_info[:10]:  # Show first 10
                print(f"    {info}")
                
        except Exception as e:
            print(f"    Error checking attributes: {e}")
        
        print(f"\n✅ Debug analysis complete!")
        
        await browser.close()

if __name__ == "__main__":
    asyncio.run(debug_rugcheck_structure())