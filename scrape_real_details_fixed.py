#!/usr/bin/env python3
"""
SIMPLIFIED product details scraper - extracts real info from source pages
Uses safer DOM queries instead of complex regex
"""
import asyncio
import json
from playwright.async_api import async_playwright

async def fetch_product_details(page, product_url):
    """Fetch detailed information using DOM queries"""
    try:
        print(f"  Loading: {product_url}")
        await page.goto(product_url, wait_until='dom contentloaded', timeout=20000)
        await asyncio.sleep(1)
        
        # Get all text content and parse it in Python
        body_text = await page.evaluate('() => document.body.innerText')
        
        # Parse dimensions
        import re
        height = re.search(r'Height[^\d]*(\d+)\s*cm', body_text, re.I)
        width = re.search(r'Width[^\d]*(\d+)\s*cm', body_text, re.I)
        depth = re.search(r'Depth[^\d]*(\d+)\s*cm', body_text, re.I)
        
        # Parse specifications
        color = re.search(r'Color:\s*([^\n]+)', body_text, re.I)
        material = re.search(r'Material:\s*([^\n]+)', body_text, re.I)
        design = re.search(r'Design:\s*([^\n]+)', body_text, re.I)
        accessories = re.search(r'Accessories:\s*([^\n]+)', body_text, re.I)
        
        return {
            'height': height.group(1) + 'cm' if height else None,
            'width': width.group(1) + 'cm' if width else None,
            'depth': depth.group(1) + 'cm' if depth else None,
            'color': color.group(1).strip() if color else None,
            'material': material.group(1).strip() if material else None,
            'design': design.group(1).strip() if design else None,
            'accessories': accessories.group(1).strip() if accessories else None
        }
    except Exception as e:
        print(f"  ⚠️  {str(e)[:50]}")
        return {}

async def main():
    with open('products_data.json', 'r', encoding='utf-8') as f:
        products = json.load(f)
    
    print(f"Enhancing {len(products)} products...\n")
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        for idx, product in enumerate(products[:10], 1):  # Test with first 10
            print(f"[{idx}/10] {product['name']}")
            details = await fetch_product_details(page, product['url'])
            
            if any(details.values()):
                if details.get('height') or details.get('width') or details.get('depth'):
                    product['dimensions'] = {
                        'height': details['height'] or 'N/A',
                        'width': details['width'] or 'N/A',
                        'depth': details['depth'] or 'N/A'
                    }
                    print(f"  ✓ Size: {details['height']} × {details['width']} × {details['depth']}")
                
                specs = {}
                if details.get('color'): 
                    specs['color'] = details['color']
                    print(f"  ✓ Color: {details['color']}")
                if details.get('material'): 
                    specs['material'] = details['material']
                if details.get('design'): 
                    specs['design'] = details['design']
                if details.get('accessories'): 
                    specs['accessories'] = details['accessories']
                
                if specs:
                    product['specifications'] = {**product.get('specifications', {}), **specs}
            
            await asyncio.sleep(0.5)
        
        await browser.close()
    
    with open('products_data.json', 'w', encoding='utf-8') as f:
        json.dump(products, f, ensure_ascii=False, indent=2)
    
    print("\n✅ Test complete - check products_data.json")

if __name__ == '__main__':
    asyncio.run(main())
