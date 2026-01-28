#!/usr/bin/env python3
"""
Comprehensive scraper to fetch complete product details from t-secondhands.jp
- Multiple product images (up to 6 per product)
- Detailed product descriptions
- Complete specifications (color, material, design, hardware, accessories, condition)
- Dimensions
- Additional metadata
"""

import asyncio
import json
import re
import time
from playwright.async_api import async_playwright

async def scrape_product_details(page, product_url):
    """
    Scrape all details for a single product
    Returns dict with images, description, specifications, etc.
    """
    try:
        await page.goto(product_url, wait_until='networkidle', timeout=30000)
        await page.wait_for_timeout(1000)
        
        # Extract all product images from the gallery
        images = []
        try:
            # Look for product gallery images
            image_elements = await page.query_selector_all('.product__media img, .product-media img, [class*="product"] img[src*="cdn.shop"]')
            
            for img in image_elements:
                src = await img.get_attribute('src')
                if src and 'cdn.shop' in src and src not in images:
                    # Clean up image URL and get high quality version
                    if '?' in src:
                        base_url = src.split('?')[0]
                        images.append(f"{base_url}?v={int(time.time())}&width=1946")
                    else:
                        images.append(src)
            
            # Limit to 6 images as observed on the site
            images = images[:6]
        except Exception as e:
            print(f"    Warning: Could not extract images: {e}")
        
        # Get the full page text for extraction
        page_text = await page.inner_text('body')
        
        # Extract description (the detailed product description)
        description = ""
        try:
            # Look for description patterns
            desc_match = re.search(r'(?:Purple|Black|Brown|Blue|Gold|Silver|Beige|Red|Green|Yellow|Orange|White|Pink).*?(?:leather|nylon|canvas|fur|PVC).*?(?:handbag|bag|shoulder|tote|clutch|backpack|pouch).*?(?:with|and).*?(?:closure|hardware|fittings|strap|chain)', page_text, re.IGNORECASE | re.DOTALL)
            if desc_match:
                description = desc_match.group(0).strip()
                # Limit description length
                if len(description) > 300:
                    description = description[:297] + "..."
        except Exception as e:
            print(f"    Warning: Could not extract description: {e}")
        
        # Extract dimensions
        dimensions = {}
        try:
            height_match = re.search(r'Height:?\s*(?:Approx\.?)?\s*(\d+\.?\d*)\s*cm', page_text, re.IGNORECASE)
            width_match = re.search(r'Width:?\s*(?:Approx\.?)?\s*(\d+\.?\d*)\s*cm', page_text, re.IGNORECASE)
            depth_match = re.search(r'Depth:?\s*(?:Approx\.?)?\s*(\d+\.?\d*)\s*cm', page_text, re.IGNORECASE)
            
            if height_match:
                dimensions['height'] = f"{height_match.group(1)}cm"
            if width_match:
                dimensions['width'] = f"{width_match.group(1)}cm"
            if depth_match:
                dimensions['depth'] = f"{depth_match.group(1)}cm"
        except Exception as e:
            print(f"    Warning: Could not extract dimensions: {e}")
        
        # Extract specifications
        specifications = {}
        additional_info = {}
        
        try:
            # Color
            color_match = re.search(r'Color[:\s]+([^\n]+)', page_text, re.IGNORECASE)
            if color_match:
                specifications['color'] = color_match.group(1).strip()
            
            # Material
            material_match = re.search(r'Material[:\s]+([^\n]+)', page_text, re.IGNORECASE)
            if material_match:
                specifications['material'] = material_match.group(1).strip()
            
            # Design
            design_match = re.search(r'Design[:\s]+([^\n]+)', page_text, re.IGNORECASE)
            if design_match:
                specifications['design'] = design_match.group(1).strip()
            
            # Hardware/Accents
            hardware_match = re.search(r'(?:Hardware|Accents)[:\s]+([^\n]+)', page_text, re.IGNORECASE)
            if hardware_match:
                specifications['hardware'] = hardware_match.group(1).strip()
            
            # Accessories
            accessories_match = re.search(r'Accessories[:\s]+([^\n]+)', page_text, re.IGNORECASE)
            if accessories_match:
                specifications['accessories'] = accessories_match.group(1).strip()
            
            # Stains/Tears
            stains_match = re.search(r'Stains/Tears[:\s]+([^\n]+)', page_text, re.IGNORECASE)
            if stains_match:
                additional_info['stainsTears'] = stains_match.group(1).strip()
            
        except Exception as e:
            print(f"    Warning: Could not extract specifications: {e}")
        
        return {
            'images': images if images else None,
            'description': description if description else None,
            'dimensions': dimensions if dimensions else None,
            'specifications': specifications if specifications else None,
            'additionalInfo': additional_info if additional_info else None
        }
        
    except Exception as e:
        print(f"    Error scraping {product_url}: {e}")
        return None

async def main():
    print("🔍 Starting comprehensive product detail scraper...")
    print("=" * 80)
    
    # Load existing products data
    products_file = 'products_data.json'
    with open(products_file, 'r', encoding='utf-8') as f:
        products = json.load(f)
    
    total_products = len(products)
    print(f"📦 Found {total_products} products to process\n")
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        )
        page = await context.new_page()
        
        start_time = time.time()
        processed = 0
        updated = 0
        
        for idx, product in enumerate(products, 1):
            product_url = product.get('url')
            if not product_url:
                print(f"⚠️  Product {idx}: No URL found, skipping")
                continue
            
            # Calculate ETA
            elapsed = time.time() - start_time
            if processed > 0:
                avg_time = elapsed / processed
                remaining = total_products - processed
                eta_seconds = avg_time * remaining
                eta_mins = eta_seconds / 60
                eta_str = f"ETA: {eta_mins:.1f} mins"
            else:
                eta_str = "Calculating ETA..."
            
            print(f"[{idx}/{total_products}] {eta_str}")
            print(f"  📄 {product.get('name', 'Unknown')[:60]}...")
            print(f"  🔗 {product_url}")
            
            # Scrape product details
            details = await scrape_product_details(page, product_url)
            
            if details:
                # Update product with new details
                if details.get('images'):
                    product['images'] = details['images']
                    print(f"  ✓ Found {len(details['images'])} images")
                
                if details.get('description'):
                    product['description'] = details['description']
                    print(f"  ✓ Description extracted")
                
                if details.get('dimensions'):
                    product['dimensions'] = details['dimensions']
                    print(f"  ✓ Dimensions: {details['dimensions']}")
                
                if details.get('specifications'):
                    # Merge with existing specifications
                    if 'specifications' not in product:
                        product['specifications'] = {}
                    product['specifications'].update(details['specifications'])
                    print(f"  ✓ Specifications updated ({len(details['specifications'])} fields)")
                
                if details.get('additionalInfo'):
                    product['additionalInfo'] = details['additionalInfo']
                    print(f"  ✓ Additional info added")
                
                updated += 1
            else:
                print(f"  ❌ Failed to scrape details")
            
            processed += 1
            print()
            
            # Save progress every 10 products
            if processed % 10 == 0:
                with open(products_file, 'w', encoding='utf-8') as f:
                    json.dump(products, f, ensure_ascii=False, indent=2)
                print(f"💾 Progress saved ({processed}/{total_products})\n")
        
        await browser.close()
    
    # Save final results
    with open(products_file, 'w', encoding='utf-8') as f:
        json.dump(products, f, ensure_ascii=False, indent=2)
    
    elapsed_time = time.time() - start_time
    print("=" * 80)
    print(f"✅ Scraping complete!")
    print(f"📊 Results:")
    print(f"   - Total products: {total_products}")
    print(f"   - Successfully updated: {updated}")
    print(f"   - Time taken: {elapsed_time/60:.1f} minutes")
    print(f"   - Average time per product: {elapsed_time/processed:.1f} seconds")
    print(f"\n💾 Updated data saved to: {products_file}")

if __name__ == '__main__':
    asyncio.run(main())
