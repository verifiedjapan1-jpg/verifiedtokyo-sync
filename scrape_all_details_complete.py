#!/usr/bin/env python3
"""
Complete product details scraper - extracts ALL information from reference pages
while preserving USD prices
"""

import asyncio
import json
import re
import time
from playwright.async_api import async_playwright

async def scrape_complete_details(page, product_url, product_id):
    """Scrape complete product details from the page"""
    try:
        print(f"  🔗 {product_url}")
        await page.goto(product_url, wait_until='networkidle', timeout=30000)
        await page.wait_for_timeout(2000)
        
        # Get the full page text
        page_text = await page.inner_text('body')
        
        details = {}
        
        # Extract full description (everything before "Thank you for viewing")
        try:
            # Look for the main product description area
            desc_patterns = [
                # Pattern 1: From color to before "Thank you"
                r'(Purple|Black|Brown|Blue|Gold|Silver|Beige|Red|Green|Yellow|Orange|White|Pink|Turquoise|Coral|Navy|Grey|Gray).*?(?:leather|nylon|canvas|fur|PVC|lambskin|calfskin|tweed).*?(?:handbag|bag|shoulder|tote|clutch|backpack|pouch|wallet).*?(?:with|featuring|and).*?(?:closure|hardware|fittings|strap|chain|zipper|buckle).*?(?:Color|Material|Design|Style|Brand|Height)',
            ]
            
            for pattern in desc_patterns:
                match = re.search(pattern, page_text, re.IGNORECASE | re.DOTALL)
                if match:
                    desc = match.group(0).strip()
                    # Clean up the description
                    desc = desc.replace('\n', ' ').strip()
                    desc = re.sub(r'\s+', ' ', desc)
                    if len(desc) > 500:
                        desc = desc[:497] + "..."
                    details['description'] = desc
                    break
            
            # If no match, try to find any descriptive text
            if 'description' not in details:
                # Look for text between product name and "Thank you"
                thank_you_pos = page_text.find('Thank you for viewing')
                if thank_you_pos > 0:
                    # Get 300 characters before "Thank you"
                    start = max(0, thank_you_pos - 300)
                    snippet = page_text[start:thank_you_pos].strip()
                    # Clean and use as description
                    snippet = re.sub(r'\s+', ' ', snippet)
                    if len(snippet) > 50:
                        details['description'] = snippet[-300:] if len(snippet) > 300 else snippet
        except Exception as e:
            print(f"    ⚠️  Description extraction failed: {e}")
        
        # Extract dimensions with better patterns
        try:
            dimensions = {}
            
            # Try multiple patterns for each dimension
            height_patterns = [
                r'Height[:\s]*(?:in cm)?[:\s]*(?:approx\.?|Approx\.?)?[:\s]*(\d+\.?\d*)\s*cm',
                r'高さ[:\s]*(?:約)?[:\s]*(\d+\.?\d*)\s*cm',
                r'H[:\s]*(\d+\.?\d*)\s*cm'
            ]
            
            width_patterns = [
                r'Width[:\s]*(?:in cm)?[:\s]*(?:approx\.?|Approx\.?)?[:\s]*(\d+\.?\d*)\s*cm',
                r'幅[:\s]*(?:約)?[:\s]*(\d+\.?\d*)\s*cm',
                r'W[:\s]*(\d+\.?\d*)\s*cm'
            ]
            
            depth_patterns = [
                r'Depth[:\s]*(?:in cm)?[:\s]*(?:approx\.?|Approx\.?)?[:\s]*(\d+\.?\d*)\s*cm',
                r'マチ[:\s]*(?:約)?[:\s]*(\d+\.?\d*)\s*cm',
                r'D[:\s]*(\d+\.?\d*)\s*cm'
            ]
            
            for pattern in height_patterns:
                match = re.search(pattern, page_text, re.IGNORECASE)
                if match:
                    dimensions['height'] = f"{match.group(1)}cm"
                    break
            
            for pattern in width_patterns:
                match = re.search(pattern, page_text, re.IGNORECASE)
                if match:
                    dimensions['width'] = f"{match.group(1)}cm"
                    break
            
            for pattern in depth_patterns:
                match = re.search(pattern, page_text, re.IGNORECASE)
                if match:
                    dimensions['depth'] = f"{match.group(1)}cm"
                    break
            
            if dimensions:
                details['dimensions'] = dimensions
                print(f"    ✓ Dimensions: {dimensions}")
        except Exception as e:
            print(f"    ⚠️  Dimensions extraction failed: {e}")
        
        # Extract specifications with better patterns
        try:
            specifications = {}
            
            # Color
            color_patterns = [
                r'Color[:\s-]+([^\n•]+)',
                r'色[:\s]+([^\n]+)',
            ]
            for pattern in color_patterns:
                match = re.search(pattern, page_text, re.IGNORECASE)
                if match:
                    color = match.group(1).strip()
                    # Clean up
                    color = re.sub(r'\s+', ' ', color)
                    specifications['color'] = color
                    break
            
            # Material
            material_patterns = [
                r'Material[:\s-]+([^\n•]+)',
                r'素材[:\s]+([^\n]+)',
            ]
            for pattern in material_patterns:
                match = re.search(pattern, page_text, re.IGNORECASE)
                if match:
                    material = match.group(1).strip()
                    material = re.sub(r'\s+', ' ', material)
                    specifications['material'] = material
                    break
            
            # Design/Style
            design_patterns = [
                r'Design[:\s-]+([^\n•]+)',
                r'Style[:\s-]+([^\n•]+)',
                r'デザイン[:\s]+([^\n]+)',
            ]
            for pattern in design_patterns:
                match = re.search(pattern, page_text, re.IGNORECASE)
                if match:
                    design = match.group(1).strip()
                    design = re.sub(r'\s+', ' ', design)
                    specifications['design'] = design
                    break
            
            # Hardware/Decoration
            hardware_patterns = [
                r'(?:Hardware|Accents|Decoration)[:\s-]+([^\n•]+)',
                r'金具[:\s]+([^\n]+)',
            ]
            for pattern in hardware_patterns:
                match = re.search(pattern, page_text, re.IGNORECASE)
                if match:
                    hardware = match.group(1).strip()
                    hardware = re.sub(r'\s+', ' ', hardware)
                    specifications['hardware'] = hardware
                    break
            
            # Accessories
            acc_patterns = [
                r'Accessories[:\s-]+([^\n•]+)',
                r'付属品[:\s]+([^\n]+)',
            ]
            for pattern in acc_patterns:
                match = re.search(pattern, page_text, re.IGNORECASE)
                if match:
                    acc = match.group(1).strip()
                    acc = re.sub(r'\s+', ' ', acc)
                    specifications['accessories'] = acc
                    break
            
            if specifications:
                details['specifications'] = specifications
                print(f"    ✓ Specs: {len(specifications)} fields")
        except Exception as e:
            print(f"    ⚠️  Specifications extraction failed: {e}")
        
        # Extract condition/stains info
        try:
            stains_patterns = [
                r'Stains[,\s]*tears[,\s]*etc\.?[:\s]+([^\n]+)',
                r'汚れ.*?[:\s]+([^\n]+)',
            ]
            for pattern in stains_patterns:
                match = re.search(pattern, page_text, re.IGNORECASE)
                if match:
                    if 'additionalInfo' not in details:
                        details['additionalInfo'] = {}
                    details['additionalInfo']['stainsTears'] = match.group(1).strip()
                    break
        except Exception as e:
            print(f"    ⚠️  Condition info extraction failed: {e}")
        
        return details if details else None
        
    except Exception as e:
        print(f"    ❌ Error: {e}")
        return None

async def main():
    print("📋 Complete Product Details Scraper")
    print("=" * 80)
    print("⚠️  USD PRICES WILL BE PRESERVED")
    print("=" * 80)
    
    # Load current products
    with open('products_data.json', 'r', encoding='utf-8') as f:
        products = json.load(f)
    
    total = len(products)
    print(f"📦 Processing {total} products\n")
    
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
                print(f"[{idx}/{total}] Skipping - no URL")
                continue
            
            # Progress
            elapsed = time.time() - start_time
            if processed > 0:
                avg_time = elapsed / processed
                remaining = total - processed
                eta_mins = (avg_time * remaining) / 60
                print(f"\n[{idx}/{total}] ETA: {eta_mins:.1f} mins")
            else:
                print(f"\n[{idx}/{total}] Starting...")
            
            print(f"  📦 {product.get('name', 'Unknown')[:60]}")
            
            # Scrape details
            details = await scrape_complete_details(page, url, product.get('id'))
            
            if details:
                # IMPORTANT: Preserve the price!
                original_price = product.get('price')
                
                # Update details
                if details.get('description'):
                    product['description'] = details['description']
                
                if details.get('dimensions'):
                    product['dimensions'] = details['dimensions']
                
                if details.get('specifications'):
                    if 'specifications' not in product:
                        product['specifications'] = {}
                    product['specifications'].update(details['specifications'])
                
                if details.get('additionalInfo'):
                    product['additionalInfo'] = details['additionalInfo']
                
                # Ensure price is still the same
                product['price'] = original_price
                
                updated += 1
                print(f"  💚 Updated (Price preserved: ${original_price})")
            else:
                print(f"  ⚠️  No details extracted")
            
            processed += 1
            
            # Save progress every 10 products
            if processed % 10 == 0:
                with open('products_data.json', 'w', encoding='utf-8') as f:
                    json.dump(products, f, ensure_ascii=False, indent=2)
                print(f"\n💾 Progress saved: {processed}/{total}")
            
            # Small delay
            await page.wait_for_timeout(800)
        
        await browser.close()
    
    # Final save
    with open('products_data.json', 'w', encoding='utf-8') as f:
        json.dump(products, f, ensure_ascii=False, indent=2)
    
    elapsed = time.time() - start_time
    print("\n" + "=" * 80)
    print("✅ COMPLETE!")
    print(f"📊 Stats:")
    print(f"   Total: {total}")
    print(f"   Updated: {updated}")
    print(f"   Time: {elapsed/60:.1f} minutes")
    print(f"   Avg/product: {elapsed/processed:.1f}s")
    print(f"\n✅ ALL USD PRICES PRESERVED!")
    print(f"💾 Saved to products_data.json")

if __name__ == '__main__':
    asyncio.run(main())
