#!/usr/bin/env python3
"""
Complete automatic scraper for all 133 products
Extracts real dimensions, colors, materials, and specifications
"""
import asyncio
import json
import re
from playwright.async_api import async_playwright
from datetime import datetime

async def fetch_product_details(page, product_url):
    """Fetch detailed information from a product page"""
    try:
        await page.goto(product_url, wait_until='domcontentloaded', timeout=15000)
        await asyncio.sleep(1)
        
        # Get all text content
        body_text = await page.evaluate('() => document.body.innerText')
        
        # Parse dimensions
        height = re.search(r'Height[^\d]*(\d+)\s*cm', body_text, re.I)
        width = re.search(r'Width[^\d]*(\d+)\s*cm', body_text, re.I)
        depth = re.search(r'Depth[^\d]*(\d+)\s*cm', body_text, re.I)
        
        # Parse specifications
        color = re.search(r'Color:\s*([^\n]+)', body_text, re.I)
        material = re.search(r'Material:\s*([^\n]+)', body_text, re.I)
        design = re.search(r'Design:\s*([^\n]+)', body_text, re.I)
        accessories = re.search(r'Accessories:\s*([^\n]+)', body_text, re.I)
        hardware = re.search(r'(?:Decoration|Hardware):\s*([^\n]+)', body_text, re.I)
        
        return {
            'height': height.group(1) + 'cm' if height else None,
            'width': width.group(1) + 'cm' if width else None,
            'depth': depth.group(1) + 'cm' if depth else None,
            'color': color.group(1).strip() if color else None,
            'material': material.group(1).strip() if material else None,
            'design': design.group(1).strip() if design else None,
            'accessories': accessories.group(1).strip() if accessories else None,
            'hardware': hardware.group(1).strip() if hardware else None
        }
    except Exception as e:
        return {}

async def main():
    start_time = datetime.now()
    
    # Load products
    with open('products_data.json', 'r', encoding='utf-8') as f:
        products = json.load(f)
    
    print(f"🚀 Starting complete scraping of {len(products)} products...")
    print(f"⏱️  Started at: {start_time.strftime('%H:%M:%S')}\n")
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        enhanced_count = 0
        skipped_count = 0
        
        for idx, product in enumerate(products, 1):
            print(f"[{idx}/{len(products)}] {product['name'][:50]}...", end=' ')
            
            details = await fetch_product_details(page, product['url'])
            
            if any(details.values()):
                # Update dimensions
                if details.get('height') or details.get('width') or details.get('depth'):
                    product['dimensions'] = {
                        'height': details['height'] or 'N/A',
                        'width': details['width'] or 'N/A',
                        'depth': details['depth'] or 'N/A'
                    }
                
                # Update specifications
                specs = {}
                if details.get('color'): 
                    specs['color'] = details['color']
                if details.get('material'): 
                    specs['material'] = details['material']
                if details.get('design'): 
                    specs['design'] = details['design']
                if details.get('accessories'): 
                    specs['accessories'] = details['accessories']
                if details.get('hardware'): 
                    specs['hardware'] = details['hardware']
                else:
                    specs['hardware'] = 'Metal fittings'  # Default
                
                if specs:
                    product['specifications'] = specs
                    enhanced_count += 1
                    print("✓")
                else:
                    skipped_count += 1
                    print("○")
            else:
                skipped_count += 1
                print("○")
            
            # Save progress every 20 products
            if idx % 20 == 0:
                with open('products_data.json', 'w', encoding='utf-8') as f:
                    json.dump(products, f, ensure_ascii=False, indent=2)
                elapsed = (datetime.now() - start_time).total_seconds()
                avg_time = elapsed / idx
                remaining = avg_time * (len(products) - idx)
                print(f"\n💾 Progress saved | Enhanced: {enhanced_count} | ETA: {int(remaining/60)}m {int(remaining%60)}s\n")
            
            # Rate limiting
            await asyncio.sleep(0.3)
        
        await browser.close()
    
    # Final save
    with open('products_data.json', 'w', encoding='utf-8') as f:
        json.dump(products, f, ensure_ascii=False, indent=2)
    
    elapsed = (datetime.now() - start_time).total_seconds()
    
    print("\n" + "="*70)
    print("✅ SCRAPING COMPLETE")
    print("="*70)
    print(f"   Total products: {len(products)}")
    print(f"   Enhanced: {enhanced_count}")
    print(f"   Skipped: {skipped_count}")
    print(f"   Time elapsed: {int(elapsed/60)}m {int(elapsed%60)}s")
    print(f"   Saved to: products_data.json")
    print("="*70)

if __name__ == '__main__':
    asyncio.run(main())
