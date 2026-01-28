#!/usr/bin/env python3
"""
Scrape ALL product images from t-secondhands.jp product pages.
This script focuses solely on extracting multiple images for each product.
"""

import asyncio
import json
import time
from playwright.async_api import async_playwright

async def scrape_product_images(page, product_url, product_id):
    """Extract all product images from a product page"""
    try:
        print(f"  🔗 Visiting: {product_url}")
        await page.goto(product_url, wait_until='networkidle', timeout=30000)
        await page.wait_for_timeout(1500)
        
        images = []
        
        # Strategy 1: Get images from thumbnail gallery (most reliable - based on HTML analysis)
        try:
            # The actual selector from the product page is .thumbnail-list img
            thumbnails = await page.query_selector_all('.thumbnail-list img, li.thumbnail-list__item img')
            for thumb in thumbnails:
                src = await thumb.get_attribute('src')
                if src and ('cdn.shop' in src or 't-secondhands.jp' in src):
                    # Handle protocol-relative URLs
                    if src.startswith('//'):
                        src = 'https:' + src
                    
                    # Get full resolution version
                    base_url = src.split('?')[0]
                    full_url = f"{base_url}?v={int(time.time())}&width=1946"
                    if full_url not in images:
                        images.append(full_url)
            
            if len(images) > 0:
                print(f"    ✓ Found {len(images)} images from thumbnails")
        except Exception as e:
            print(f"    ⚠️  Thumbnail strategy failed: {e}")
        
        # Strategy 2: Get from main product media gallery (backup)
        if len(images) == 0:
            try:
                # Use the actual selector from HTML analysis: .product__media-list .product__media img
                media_imgs = await page.query_selector_all('.product__media-list .product__media img, .product__media-item img.image-magnify-lightbox')
                for img in media_imgs:
                    src = await img.get_attribute('src')
                    if src and ('cdn.shop' in src or 't-secondhands.jp' in src):
                        if src.startswith('//'):
                            src = 'https:' + src
                        
                        base_url = src.split('?')[0]
                        full_url = f"{base_url}?v={int(time.time())}&width=1946"
                        if full_url not in images:
                            images.append(full_url)
                
                if len(images) > 0:
                    print(f"    ✓ Found {len(images)} images from media gallery")
            except Exception as e:
                print(f"    ⚠️  Media gallery strategy failed: {e}")
        
        # Strategy 3: Parse srcset for high-resolution images (additional backup)
        if len(images) == 0:
            try:
                srcset_imgs = await page.query_selector_all('.product__media-list img[srcset]')
                for img in srcset_imgs:
                    srcset = await img.get_attribute('srcset')
                    if srcset and 'cdn.shop' in srcset:
                        # Parse srcset to get the largest image
                        parts = srcset.split(',')
                        for part in parts:
                            url = part.strip().split(' ')[0]
                            if 'cdn.shop' in url:
                                if url.startswith('//'):
                                    url = 'https:' + url
                                base_url = url.split('?')[0]
                                full_url = f"{base_url}?v={int(time.time())}&width=1946"
                                if full_url not in images:
                                    images.append(full_url)
                
                if len(images) > 0:
                    print(f"    ✓ Found {len(images)} images from srcset")
            except Exception as e:
                print(f"    ⚠️  Srcset strategy failed: {e}")

        
        # Remove duplicates and limit to 8 images
        images = list(dict.fromkeys(images))[:8]
        
        if images:
            print(f"  ✅ Found {len(images)} images for product {product_id}")
            return images
        else:
            print(f"  ⚠️  No images found for product {product_id}")
            return None
            
    except Exception as e:
        print(f"  ❌ Error for product {product_id}: {e}")
        return None

async def main():
    print("🖼️  Starting multi-image scraper for all products")
    print("=" * 80)
    
    # Load products
    with open('products_data.json', 'r', encoding='utf-8') as f:
        products = json.load(f)
    
    total = len(products)
    print(f"📦 Found {total} products to process\n")
    
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
            
            # Scrape images
            images = await scrape_product_images(page, url, product.get('id'))
            
            if images and len(images) > 0:
                product['images'] = images
                updated += 1
                print(f"  💚 Updated with {len(images)} images")
            else:
                # Fallback to single imageUrl
                if product.get('imageUrl'):
                    product['images'] = [product['imageUrl']]
                    print(f"  💛 Using fallback single image")
            
            processed += 1
            print()
            
            # Save every 5 products
            if processed % 5 == 0:
                with open('products_data.json', 'w', encoding='utf-8') as f:
                    json.dump(products, f, ensure_ascii=False, indent=2)
                print(f"💾 Progress saved: {processed}/{total}\n")
            
            # Small delay between requests
            await page.wait_for_timeout(500)
        
        await browser.close()
    
    # Final save
    with open('products_data.json', 'w', encoding='utf-8') as f:
        json.dump(products, f, ensure_ascii=False, indent=2)
    
    elapsed = time.time() - start_time
    print("=" * 80)
    print("✅ Scraping completed!")
    print(f"📊 Stats:")
    print(f"   Total products: {total}")
    print(f"   Successfully updated: {updated}")
    print(f"   Time: {elapsed/60:.1f} minutes")
    print(f"   Avg per product: {elapsed/processed:.1f}s")
    print(f"\n💾 Saved to products_data.json")

if __name__ == '__main__':
    asyncio.run(main())
