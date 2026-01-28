#!/usr/bin/env python3
"""
Scrape structured detail text from t-secondhands.jp product pages
Extracts: intro, dimensions, description, specs, closing, additional info
"""

import asyncio
import json
import re
from playwright.async_api import async_playwright

async def extract_detail_text(page, url):
    """Extract structured detail text from product page"""
    try:
        await page.goto(url, wait_until='networkidle', timeout=30000)
        await page.wait_for_timeout(2000)
        
        # Get the product description section
        description_selectors = [
            '.product__description',
            '.product-single__description',
            '[class*="description"]',
            '.rte'
        ]
        
        detail_text = None
        for selector in description_selectors:
            elements = await page.query_selector_all(selector)
            for elem in elements:
                text = await elem.inner_text()
                if text and len(text) > 100:  # Long enough to be product description
                    detail_text = text
                    break
            if detail_text:
                break
        
        if not detail_text:
            print(f"    ⚠️  No description text found")
            return None
        
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
        
        # Extract intro message (first 4 lines typically)
        intro_lines = []
        i = 0
        while i < len(lines) and i < 6:
            line = lines[i]
            # Stop at dimensions
            if 'Height' in line or 'Width' in line or 'Depth' in line:
                break
            # Stop at bullet points
            if line.startswith('-') or line.startswith('•'):
                break
            intro_lines.append(line)
            i += 1
        
        result['intro'] = '\n'.join(intro_lines)
        
        # Extract dimensions
        dim_text = detail_text
        height_match = re.search(r'Height\s+in\s+cm:\s*([^\n]+)', dim_text, re.IGNORECASE)
        if height_match:
            result['dimensions']['height'] = height_match.group(1).strip()
        
        width_match = re.search(r'Width\s+([^\n]+?)(?:Depth|$)', dim_text, re.IGNORECASE)
        if width_match:
            result['dimensions']['width'] = width_match.group(1).strip()
        
        depth_match = re.search(r'Depth:\s*([^\n]+)', dim_text, re.IGNORECASE)
        if depth_match:
            result['dimensions']['depth'] = depth_match.group(1).strip()
        
        # Extract short description (line after dimensions, before bullet points)
        desc_found = False
        for idx, line in enumerate(lines):
            if 'Depth' in line:
                # Next non-empty line is likely the description
                if idx + 1 < len(lines):
                    next_line = lines[idx + 1]
                    if not next_line.startswith('-') and not next_line.startswith('•'):
                        result['description'] = next_line
                        desc_found = True
                break
        
        # If not found after depth, look for a substantial line between dimensions and specs
        if not desc_found:
            for line in lines:
                if line.startswith('-') or line.startswith('•'):
                    break
                if len(line) > 30 and 'Height' not in line and 'Width' not in line and 'Depth' not in line:
                    if not any(intro in line for intro in ['Available', 'update', 'Thank you for your understanding']):
                        result['description'] = line
                        break
        
        # Extract specifications (bullet points)
        specs = []
        in_specs = False
        for line in lines:
            if line.startswith('-') or line.startswith('•'):
                in_specs = True
                # Remove bullet and clean
                spec = line[1:].strip() if line.startswith('-') else line[1:].strip()
                specs.append(spec)
            elif in_specs and ':' in line and len(line) < 100:
                # Might be continuation of specs
                specs.append(line)
            elif in_specs and 'Thank you' in line:
                # End of specs
                break
        
        result['specifications'] = specs
        
        # Extract closing message
        for line in lines:
            if 'Thank you for visiting' in line:
                result['closing'] = line
                break
        
        # Extract additional info (Color, Accessories, Stains)
        additional_parts = []
        for line in lines:
            if 'Accessories:' in line or 'Stains' in line or ('Color:' in line and 'Stains' in line):
                # This is the additional info line
                result['additional'] = line
                break
        
        return result
        
    except Exception as e:
        print(f"    ❌ Error extracting detail text: {e}")
        return None

async def scrape_all_detail_texts():
    """Scrape detail text for all products"""
    
    # Load existing products
    try:
        with open('products_data.json', 'r', encoding='utf-8') as f:
            products = json.load(f)
    except FileNotFoundError:
        print("❌ products_data.json not found")
        return
    
    print(f"📚 Loading detail text for {len(products)} products...")
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        )
        page = await context.new_page()
        
        updated_count = 0
        failed_count = 0
        
        for idx, product in enumerate(products, 1):
            product_url = product.get('url')
            if not product_url:
                print(f"{idx}. ⚠️  No URL for product {product.get('name', 'Unknown')}")
                failed_count += 1
                continue
            
            print(f"{idx}. Scraping detail text: {product.get('name', 'Unknown')[:50]}...")
            
            detail_text = await extract_detail_text(page, product_url)
            
            if detail_text:
                # Preserve original price
                original_price = product.get('price')
                
                # Update product
                product['detailText'] = detail_text
                product['price'] = original_price
                
                print(f"    ✅ Detail text extracted")
                print(f"       Intro: {'✓' if detail_text['intro'] else '✗'}")
                print(f"       Dimensions: {'✓' if detail_text['dimensions']['height'] else '✗'}")
                print(f"       Description: {'✓' if detail_text['description'] else '✗'}")
                print(f"       Specs: {len(detail_text['specifications'])} items")
                updated_count += 1
            else:
                print(f"    ❌ Failed to extract detail text")
                failed_count += 1
            
            # Save progress every 10 products
            if idx % 10 == 0:
                with open('products_data.json', 'w', encoding='utf-8') as f:
                    json.dump(products, f, indent=2, ensure_ascii=False)
                print(f"💾 Progress saved ({idx}/{len(products)})")
        
        await browser.close()
    
    # Final save
    with open('products_data.json', 'w', encoding='utf-8') as f:
        json.dump(products, f, indent=2, ensure_ascii=False)
    
    print(f"\n✅ Complete!")
    print(f"   Updated: {updated_count}/{len(products)}")
    print(f"   Failed: {failed_count}/{len(products)}")
    print(f"   Success rate: {updated_count/len(products)*100:.1f}%")

if __name__ == '__main__':
    asyncio.run(scrape_all_detail_texts())
