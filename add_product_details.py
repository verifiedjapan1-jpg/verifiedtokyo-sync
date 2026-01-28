#!/usr/bin/env python3
"""
Enhanced product sync that includes all details in one pass
Combines sync_products.py with detailed scraping
"""
import asyncio
import json
import re
from playwright.async_api import async_playwright

async def scrape_product_full_details(page, product_url):
    """Scrape full product details including price, description, dimensions, specs"""
    try:
        await page.goto(product_url, wait_until='networkidle', timeout=30000)
        await asyncio.sleep(1)
        
        # Get page text for extraction
        page_text = await page.inner_text('body')
        
        # Extract title
        title = await page.eval_on_selector('h1', 'el => el?.textContent?.trim() || ""')
        title = title.replace(' – T-Family', '').strip()
        
        # Extract USD price
        price_el = await page.query_selector('.price, .product-price, [class*="price"]')
        price_text = await price_el.inner_text() if price_el else ''
        usd_match = re.search(r'\$([\\d,]+(?:\\.\\d{2})?)\\s*USD', price_text, re.IGNORECASE)
        price_usd = 0
        if usd_match:
            price_usd = float(usd_match.group(1).replace(',', ''))
        
        # Extract image
        img_el = await page.query_selector('img[src*="cdn"], img[src*="products"]')
        image_url = await img_el.get_attribute('src') if img_el else ''
        
        # Extract description
        description = ""
        desc_match = re.search(r'(?:Purple|Black|Brown|Blue|Gold|Silver|Beige|Red|Green|Yellow|Orange|White|Pink|Turquoise|Cream).*?(?:leather|nylon|canvas|fur|PVC).*?(?:handbag|bag|shoulder|tote|clutch|backpack|pouch|wallet)', page_text, re.IGNORECASE | re.DOTALL)
        if desc_match:
            description = desc_match.group(0).strip()[:300]
        
        # Extract dimensions
        dimensions = {}
        height_match = re.search(r'Height:?\\s*(?:Approx\\.?)?\\s*(\\d+\\.?\\d*)\\s*cm', page_text, re.IGNORECASE)
        width_match = re.search(r'Width:?\\s*(?:Approx\\.?)?\\s*(\\d+\\.?\\d*)\\s*cm', page_text, re.IGNORECASE)
        depth_match = re.search(r'Depth:?\\s*(?:Approx\\.?)?\\s*(\\d+\\.?\\d*)\\s*cm', page_text, re.IGNORECASE)
        
        if height_match:
            dimensions['height'] = f"{height_match.group(1)}cm"
        if width_match:
            dimensions['width'] = f"{width_match.group(1)}cm"
        if depth_match:
            dimensions['depth'] = f"{depth_match.group(1)}cm"
        
        # Extract specifications
        specifications = {}
        color_match = re.search(r'Color[:\\s]+([^\\n]+)', page_text, re.IGNORECASE)
        if color_match:
            specifications['color'] = color_match.group(1).strip()
        
        material_match = re.search(r'Material[:\\s]+([^\\n]+)', page_text, re.IGNORECASE)
        if material_match:
            specifications['material'] = material_match.group(1).strip()
        
        design_match = re.search(r'Design[:\\s]+([^\\n]+)', page_text, re.IGNORECASE)
        if design_match:
            specifications['design'] = design_match.group(1).strip()
        
        hardware_match = re.search(r'(?:Hardware|Accents)[:\\s]+([^\\n]+)', page_text, re.IGNORECASE)
        if hardware_match:
            specifications['hardware'] = hardware_match.group(1).strip()
        
        accessories_match = re.search(r'Accessories[:\\s]+([^\\n]+)', page_text, re.IGNORECASE)
        if accessories_match:
            specifications['accessories'] = accessories_match.group(1).strip()
        
        return {
            'title': title,
            'priceUSD': price_usd,
            'imageUrl': image_url,
            'description': description if description else None,
            'dimensions': dimensions if dimensions else None,
            'specifications': specifications if specifications else None
        }
        
    except Exception as e:
        print(f"    ✗ Error: {e}")
        return None

async def sync_with_full_details():
    print("\\n" + "="*60)
    print("🔄 SYNCING PRODUCTS WITH FULL DETAILS")
    print("="*60 + "\\n")
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        # Load existing products to get URLs
        with open('products_data.json', 'r', encoding='utf-8') as f:
            products = json.load(f)
        
        total = len(products)
        print(f"📦 Processing {total} products\\n")
        
        # Update each product with full details
        for idx, product in enumerate(products, 1):
            print(f"[{idx}/{total}] {product['name'][:50]}...")
            
            details = await scrape_product_full_details(page, product['url'])
            
            if details:
                # Update product with new details
                if details.get('description'):
                    product['description'] = details['description']
                    print(f"  ✓ Description added")
                
                if details.get('dimensions'):
                    product['dimensions'] = details['dimensions']
                    print(f"  ✓ Dimensions: {details['dimensions']}")
                
                if details.get('specifications'):
                    # Merge with existing specs if any
                    if 'specifications' not in product:
                        product['specifications'] = {}
                    product['specifications'].update(details['specifications'])
                    print(f"  ✓ Specifications: {len(details['specifications'])} fields")
                
                print()
            
            # Save progress every 10 products
            if idx % 10 == 0:
                with open('products_data.json', 'w', encoding='utf-8') as f:
                    json.dump(products, f, ensure_ascii=False, indent=2)
                print(f"💾 Progress saved ({idx}/{total})\\n")
        
        await browser.close()
    
    # Save final results
    with open('products_data.json', 'w', encoding='utf-8') as f:
        json.dump(products, f, ensure_ascii=False, indent=2)
    
    print("="*60)
    print("✅ SYNC COMPLETED")
    print(f"📦 Updated {total} products with full details\\n")

if __name__ == '__main__':
    asyncio.run(sync_with_full_details())
