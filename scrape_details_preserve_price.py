#!/usr/bin/env python3
"""
Scrape detailed product information from t-secondhands.jp
WITHOUT changing existing USD prices
"""

import asyncio
import json
import re
import time
from playwright.async_api import async_playwright

async def scrape_product_details(page, product_url, product_id):
    """Scrape product details without touching the price"""
    try:
        print(f"  🔗 Visiting: {product_url}")
        await page.goto(product_url, wait_until='networkidle', timeout=30000)
        await page.wait_for_timeout(1500)
        
        # Get the full page text for extraction
        page_text = await page.inner_text('body')
        
        details = {}
        
        # Extract description
        try:
            # Look for product description in various patterns
            desc_patterns = [
                r'(?:Purple|Black|Brown|Blue|Gold|Silver|Beige|Red|Green|Yellow|Orange|White|Pink|Turquoise|Coral).*?(?:leather|nylon|canvas|fur|PVC|lambskin|calfskin).*?(?:handbag|bag|shoulder|tote|clutch|backpack|pouch|wallet).*?(?:with|and|featuring).*?(?:closure|hardware|fittings|strap|chain|zipper)',
                r'Brand:.*?(?:Color|Material|Design|Style|Accessories)',
            ]
            
            for pattern in desc_patterns:
                desc_match = re.search(pattern, page_text, re.IGNORECASE | re.DOTALL)
                if desc_match:
                    description = desc_match.group(0).strip()
                    # Limit description length
                    if len(description) > 300:
                        description = description[:297] + "..."
                    details['description'] = description
                    break
        except Exception as e:
            print(f"    ⚠️  Could not extract description: {e}")
        
        # Extract dimensions
        try:
            dimensions = {}
            height_match = re.search(r'Height:?\\s*(?:Approx\\.?|approx\\.?)?\\s*(\\d+\\.?\\d*)\\s*cm', page_text, re.IGNORECASE)
            width_match = re.search(r'Width:?\\s*(?:Approx\\.?|approx\\.?)?\\s*(\\d+\\.?\\d*)\\s*cm', page_text, re.IGNORECASE)
            depth_match = re.search(r'Depth:?\\s*(?:Approx\\.?|approx\\.?)?\\s*(\\d+\\.?\\d*)\\s*cm', page_text, re.IGNORECASE)
            
            if height_match:
                dimensions['height'] = f"{height_match.group(1)}cm"
            if width_match:
                dimensions['width'] = f"{width_match.group(1)}cm"
            if depth_match:
                dimensions['depth'] = f"{depth_match.group(1)}cm"
            
            if dimensions:
                details['dimensions'] = dimensions
                print(f"    ✓ Dimensions: H={dimensions.get('height', 'N/A')} W={dimensions.get('width', 'N/A')} D={dimensions.get('depth', 'N/A')}")
        except Exception as e:
            print(f"    ⚠️  Could not extract dimensions: {e}")
        
        # Extract specifications
        try:
            specifications = {}
            
            # Color
            color_match = re.search(r'Color[:\\s-]+([^\\n]+)', page_text, re.IGNORECASE)
            if color_match:
                specifications['color'] = color_match.group(1).strip()
            
            # Material
            material_match = re.search(r'Material[:\\s-]+([^\\n]+)', page_text, re.IGNORECASE)
            if material_match:
                specifications['material'] = material_match.group(1).strip()
            
            # Design
            design_match = re.search(r'Design[:\\s-]+([^\\n]+)', page_text, re.IGNORECASE)
            if design_match:
                specifications['design'] = design_match.group(1).strip()
            
            # Hardware/Accents
            hardware_match = re.search(r'(?:Hardware|Accents|Decoration)[:\\s-]+([^\\n]+)', page_text, re.IGNORECASE)
            if hardware_match:
                specifications['hardware'] = hardware_match.group(1).strip()
            
            # Accessories
            accessories_match = re.search(r'Accessories[:\\s-]+([^\\n]+)', page_text, re.IGNORECASE)
            if accessories_match:
                specifications['accessories'] = accessories_match.group(1).strip()
            
            if specifications:
                details['specifications'] = specifications
                print(f"    ✓ Specifications: {len(specifications)} fields")
        except Exception as e:
            print(f"    ⚠️  Could not extract specifications: {e}")
        
        # Extract additional info
        try:
            additional_info = {}
            stains_match = re.search(r'Stains/Tears[:\\s-]+([^\\n]+)', page_text, re.IGNORECASE)
            if stains_match:
                additional_info['stainsTears'] = stains_match.group(1).strip()
            
            if additional_info:
                details['additionalInfo'] = additional_info
        except Exception as e:
            print(f"    ⚠️  Could not extract additional info: {e}")
        
        return details if details else None
        
    except Exception as e:
        print(f"    ❌ Error scraping {product_url}: {e}")
        return None

async def main():
    print("📋 Starting product details scraper (preserving prices)")
    print("=" * 80)
    
    # Load products
    with open('products_data.json', 'r', encoding='utf-8') as f:
        products = json.load(f)
    
    total = len(products)
    print(f"📦 Found {total} products to process\\n")
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        )
        page = await context.new_page()
        
        start_time = time.time()
        processed = 0
        updated = 0
        
        for idx, product in enumerate(products, 1):
            url = product.get('url')
            if not url:
                continue
            
            # Progress display
            elapsed = time.time() - start_time
            if processed > 0:
                avg_time = elapsed / processed
                remaining = total - processed
                eta_mins = (avg_time * remaining) / 60
                print(f"[{idx}/{total}] Processing... ETA: {eta_mins:.1f} mins")
            else:
                print(f"[{idx}/{total}] Starting...")
            
            print(f"  📦 {product.get('name', 'Unknown')[:65]}")
            
            # Scrape details
            details = await scrape_product_details(page, url, product.get('id'))
            
            if details:
                # Update product with new details (but preserve price!)
                if details.get('description'):
                    product['description'] = details['description']
                
                if details.get('dimensions'):
                    product['dimensions'] = details['dimensions']
                
                if details.get('specifications'):
                    # Merge with existing specifications
                    if 'specifications' not in product:
                        product['specifications'] = {}
                    product['specifications'].update(details['specifications'])
                
                if details.get('additionalInfo'):
                    product['additionalInfo'] = details['additionalInfo']
                
                updated += 1
                print(f"  💚 Updated product details")
            
            processed += 1
            print()
            
            # Save every 10 products
            if processed % 10 == 0:
                with open('products_data.json', 'w', encoding='utf-8') as f:
                    json.dump(products, f, ensure_ascii=False, indent=2)
                print(f"💾 Progress saved: {processed}/{total}\\n")
            
            # Small delay between requests
            await page.wait_for_timeout(500)
        
        await browser.close()
    
    # Final save
    with open('products_data.json', 'w', encoding='utf-8') as f:
        json.dump(products, f, ensure_ascii=False, indent=2)
    
    elapsed = time.time() - start_time
    print("=" * 80)
    print("✅ Detail scraping completed!")
    print(f"📊 Stats:")
    print(f"   Total products: {total}")
    print(f"   Successfully updated: {updated}")
    print(f"   Time: {elapsed/60:.1f} minutes")
    print(f"   Avg per product: {elapsed/processed:.1f}s")
    print(f"\\n💾 Saved to products_data.json")
    print(f"\\n✅ All prices preserved in USD!")

if __name__ == '__main__':
    asyncio.run(main())
