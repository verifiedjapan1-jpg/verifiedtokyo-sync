#!/usr/bin/env python3
"""
Test script to verify detail text extraction on first product only
"""

import asyncio
import json
from playwright.async_api import async_playwright
import re

async def extract_detail_text(page, url):
    """Extract structured detail text from product page"""
    try:
        print(f"   Loading page: {url}")
        await page.goto(url, wait_until='networkidle', timeout=30000)
        await page.wait_for_timeout(2000)
        
        # Get the product description section - try multiple sele ctors
        description_selectors = [
            '.product__description',
            '.product-single__description', 
            '[class*="description"]',
            '.rte',
            '.product-description'
        ]
        
        detail_text = None
        for selector in description_selectors:
            try:
                elements = await page.query_selector_all(selector)
                for elem in elements:
                    text = await elem.inner_text()
                    if text and len(text) > 50:
                        detail_text = text
                        print(f"   Found text with selector: {selector}")
                        print(f"   Text length: {len(text)} chars")
                        break
                if detail_text:
                    break
            except:
                continue
        
        if not detail_text:
            print(f"   ⚠️  No description found, trying full page text")
            detail_text = await page.inner_text('body')
        
        print(f"\n   Raw text:\n{detail_text[:500]}...\n")
        
        # Parse the structured text
        lines = [line.strip() for line in detail_text.split('\n') if line.strip()]
        
        result = {
            'intro': '',
            'dimensions': {
                'height': '',
                'width': '',
                'depth': ''
            },
            'description': '',
            'specifications': [],
            'closing': '',
            'additional': ''
        }
        
        # Extract intro message
        intro_lines = []
        for i, line in enumerate(lines[:10]):
            if 'Height' in line or 'Width' in line or 'Depth' in line:
                break
            if line.startswith('-') or line.startswith('•'):
                break
            if len(line) > 10 and 'Available' in line or 'update' in line or 'understanding' in line:
                intro_lines.append(line)
        
        if intro_lines:
            result['intro'] = '\n'.join(intro_lines[:4])
        
        # Extract dimensions
        for line in lines:
            if 'Height' in line and 'cm' in line:
                match = re.search(r'Height[^:]*:\s*([^\n]+)', line, re.IGNORECASE)
                if match:
                    result['dimensions']['height'] = match.group(1).strip()
            
            if 'Width' in line and 'cm' in line:
                match = re.search(r'Width\s+([^\n]+?)(?:Depth|$)', line, re.IGNORECASE)
                if match:
                    result['dimensions']['width'] = match.group(1).strip()
                elif 'Width' in line:
                    parts = line.split('Width')
                    if len(parts) > 1:
                        result['dimensions']['width'] = parts[1].strip()
            
            if 'Depth' in line and 'cm' in line:
                match = re.search(r'Depth:\s*([^\n]+)', line, re.IGNORECASE)
                if match:
                    result['dimensions']['depth'] = match.group(1).strip()
        
        # Extract description - look for line with "leather" or product keywords
        for idx, line in enumerate(lines):
            if len(line) > 30 and len(line) < 200:
                if any(word in line.lower() for word in ['leather', 'handbag', 'bag', 'closure', 'hardware']):
                    if not line.startswith('-') and 'Height' not in line and 'Width' not in line:
                        if 'Available' not in line and 'Thank you' not in line:
                            result['description'] = line
                            break
        
        # Extract specifications (lines starting with -)
        for line in lines:
            if line.startswith('-') and ':' in line:
                spec = line[1:].strip()
                result['specifications'].append(spec)
        
        # Extract closing
        for line in lines:
            if 'Thank you for visiting' in line:
                result['closing'] = line
                break
        
        # Extract additional info
        for line in lines:
            if 'Accessories:' in line or ('Color:' in line and ('Stains' in line or 'Accessories' in line)):
                result['additional'] = line
                break
        
        return result
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return None

async def test_first_product():
    """Test scraping on first product"""
    
    # Load products
    with open('products_data.json', 'r') as f:
        products = json.load(f)
    
    product = products[0]
    print(f"Testing extraction on: {product['name']}")
    print(f"URL: {product['url']}\n")
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()
        
        detail_text = await extract_detail_text(page, product['url'])
        
        if detail_text:
            print("\n✅ Extracted detail text:")
            print(f"\nIntro:\n{detail_text['intro']}\n")
            print(f"Dimensions:")
            print(f"  Height: {detail_text['dimensions']['height']}")
            print(f"  Width: {detail_text['dimensions']['width']}")
            print(f"  Depth: {detail_text['dimensions']['depth']}\n")
            print(f"Description:\n{detail_text['description']}\n")
            print(f"Specifications ({len(detail_text['specifications'])} items):")
            for spec in detail_text['specifications']:
                print(f"  - {spec}")
            print(f"\nClosing:\n{detail_text['closing']}\n")
            print(f"Additional:\n{detail_text['additional']}\n")
        else:
            print("\n❌ Failed to extract")
        
        await browser.close()

if __name__ == '__main__':
    asyncio.run(test_first_product())
