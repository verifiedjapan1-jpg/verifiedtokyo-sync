#!/usr/bin/env python3
"""
Enhanced product scraper that extracts REAL product details from each product page
- Dimensions (height, width, depth)
- Color, Material, Design
- Condition notes
- All other specifications
"""
import asyncio
import json
import re
from playwright.async_api import async_playwright
from datetime import datetime

async def fetch_product_details(page, product_url):
    """Fetch detailed information from a single product page"""
    try:
        print(f"  Fetching details from: {product_url}")
        await page.goto(product_url, wait_until='networkidle', timeout=30000)
        await asyncio.sleep(2)
        
        details = await page.evaluate('''
            () => {
                // Extract all text from the page
                const bodyText = document.body.innerText;
                
                // Try to find dimensions (Height, Width, Depth)
                const heightMatch = bodyText.match(/Height.*?(\d+)\s*cm/i);
                const widthMatch = bodyText.match(/Width.*?(\d+)\s*cm/i);
                const depthMatch = bodyText.match(/Depth.*?(\d+)\s*cm/i);
                
                // Try to find color
                const colorMatch = bodyText.match(/Color:\s*([^\n]+)/i);
                
                // Try to find material
                const materialMatch = bodyText.match(/Material:\s*([^\n]+)/i);
                
                // Try to find design
                const designMatch = bodyText.match(/Design:\s*([^\n]+)/i);
                
                // Try to find accessories
                const accessoriesMatch = bodyText.match(/Accessories:\s*([^\n]+)/i);
                
                // Try to find condition/stains
                const stainsMatch = bodyText.match(/Stains.*?:\s*([^\n]+)/i);
                
                return {
                    height: heightMatch ? heightMatch[1] + 'cm' : null,
                    width: widthMatch ? widthMatch[1] + 'cm' : null,
                    depth: depthMatch ? depthMatch[1] + 'cm' : null,
                    color: colorMatch ? colorMatch[1].trim() : null,
                    material: materialMatch ? materialMatch[1].trim() : null,
                    design: designMatch ? designMatch[1].trim() : null,
                    accessories: accessoriesMatch ? accessoriesMatch[1].trim() : null,
                    condition_notes: stainsMatch ? stainsMatch[1].trim() : null,
                    bodySnippet: bodyText.substring(0, 500)
                };
            }
        ''')
        
        return details
    except Exception as e:
        print(f"  ⚠️  Error fetching details: {e}")
        return None

async def enhance_all_products():
    """Enhance all products with detailed information from their pages"""
    # Read current products
    with open('products_data.json', 'r', encoding='utf-8') as f:
        products = json.load(f)
    
    print(f"Enhancing {len(products)} products with real details...")
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        enhanced_count = 0
        
        for idx, product in enumerate(products, 1):
            print(f"\n[{idx}/{len(products)}] {product['name']}")
            
            # Fetch details from product URL
            details = await fetch_product_details(page, product['url'])
            
            if details:
                # Update dimensions
                if details['height'] or details['width'] or details['depth']:
                    product['dimensions'] = {
                        'height': details['height'] or 'N/A',
                        'width': details['width'] or 'N/A',
                        'depth': details['depth'] or 'N/A',
                        'unit': 'cm'
                    }
                    print(f"  ✓ Dimensions: {details['height']} x {details['width']} x {details['depth']}")
                
                # Update specifications
                product['specifications'] = {}
                
                if details['color']:
                    product['specifications']['color'] = details['color']
                    print(f"  ✓ Color: {details['color']}")
                
                if details['material']:
                    product['specifications']['material'] = details['material']
                    print(f"  ✓ Material: {details['material']}")
                
                if details['design']:
                    product['specifications']['design'] = details['design']
                    print(f"  ✓ Design: {details['design']}")
                
                if details['accessories']:
                    product['specifications']['accessories'] = details['accessories']
                    print(f"  ✓ Accessories: {details['accessories']}")
                
                if details['condition_notes']:
                    product['specifications']['condition_notes'] = details['condition_notes']
                    print(f"  ✓ Condition: {details['condition_notes']}")
                
                # Add hardware as default
                if not product['specifications'].get('hardware'):
                    product['specifications']['hardware'] = 'Metal fittings'
                
                enhanced_count += 1
            
            # Rate limiting
            await asyncio.sleep(1)
            
            # Save progress every 10 products
            if idx % 10 == 0:
                with open('products_data.json', 'w', encoding='utf-8') as f:
                    json.dump(products, f, ensure_ascii=False, indent=2)
                print(f"\n💾 Progress saved ({idx}/{len(products)})")
        
        await browser.close()
    
    # Final save
    with open('products_data.json', 'w', encoding='utf-8') as f:
        json.dump(products, f, ensure_ascii=False, indent=2)
    
    print("\n" + "="*60)
    print(f"✅ ENHANCEMENT COMPLETE")
    print("="*60)
    print(f"   Enhanced: {enhanced_count}/{len(products)} products")
    print(f"   Saved to: products_data.json")

if __name__ == '__main__':
    asyncio.run(enhance_all_products())
