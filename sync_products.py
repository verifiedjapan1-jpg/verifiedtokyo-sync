#!/usr/bin/env python3
"""
Auto-sync products from t-secondhands.jp
Detects new products and updates all necessary files
"""
import asyncio
import json
import re
from datetime import datetime
from playwright.async_api import async_playwright

async def fetch_latest_products():
    """Scrape all products from t-secondhands.jp using pagination"""
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        all_products_data = []
        current_page = 1
        
        while True:
            url = f'https://t-secondhands.jp/ja/collections/all?page={current_page}'
            print(f"🌐 Page {current_page}: {url}")
            
            try:
                await page.goto(url, wait_until='networkidle', timeout=30000)
                await asyncio.sleep(2)
                
                # Extract products from current page
                products_data = await page.evaluate('''
                    () => {
                        const products = [];
                        const productLinks = document.querySelectorAll('a[href*="/products/"]');
                        const seen = new Set();
                        
                        productLinks.forEach((link) => {
                            const url = link.href;
                            if (url.includes('/products/') && !url.includes('/collections/') && !seen.has(url)) {
                                seen.add(url);
                                products.push({ url: url });
                            }
                        });
                        
                        return products;
                    }
                ''')
                
                if not products_data:
                    print(f"  ✓ No more products. Done!")
                    break
                
                print(f"  ✓ Found {len(products_data)} products")
                all_products_data.extend(products_data)
                current_page += 1
                
            except Exception as e:
                print(f"  ✗ Error: {e}")
                break
        
        print(f"\n📦 Total URLs: {len(all_products_data)}")
        
        # Scrape details
        all_products = []
        for idx, prod in enumerate(all_products_data, 1):
            print(f"[{idx}/{len(all_products_data)}] Fetching...", end=' ')
            
            try:
                await page.goto(prod['url'], wait_until='networkidle', timeout=10000)
                
                product_details = await page.evaluate('''
                    () => {
                        const title = document.querySelector('h1')?.textContent?.trim() || '';
                        
                        // Extract USD price (format: $175.00 USD or $175 USD)
                        const priceEl = document.querySelector('.price, .product-price, [class*="price"]');
                        const priceText = priceEl?.textContent?.trim() || '';
                        
                        // Match USD price pattern: $175.00 USD or $175 USD
                        const usdMatch = priceText.match(/\\$([\\d,]+(?:\\.\\d{2})?)\\s*USD/i);
                        let priceUSD = 0;
                        if (usdMatch) {
                            priceUSD = parseFloat(usdMatch[1].replace(/,/g, ''));
                        } else {
                            // Fallback: try to find any dollar amount
                            const dollarMatch = priceText.match(/\\$([\\d,]+(?:\\.\\d{2})?)/);
                            if (dollarMatch) {
                                priceUSD = parseFloat(dollarMatch[1].replace(/,/g, ''));
                            }
                        }
                        
                        const imgEl = document.querySelector('img[src*="cdn"], img[src*="products"]');
                        const imageUrl = imgEl?.src || '';
                        
                        return {
                            title: title.replace(' – T-Family', '').trim(),
                            priceUSD: priceUSD,
                            imageUrl: imageUrl
                        };
                    }
                ''')
                
                brand = product_details['title'].split()[0] if product_details['title'] else 'UNKNOWN'
                
                # Add $200 markup to original USD price
                original_usd = product_details['priceUSD']
                markup_price = original_usd + 200
                
                product = {
                    'id': idx,
                    'name': product_details['title'],
                    'brand': brand.upper(),
                    'price': markup_price,  # Now in USD, not JPY thousands
                    'url': prod['url'],
                    'imageUrl': product_details['imageUrl'],
                    'productId': prod['url'].split('/')[-1]
                }
                
                all_products.append(product)
                print(f"✓ {brand} ${original_usd:.0f} → ${markup_price:.0f}")
                
            except Exception as e:
                print(f"✗ {e}")
        
        await browser.close()
        return all_products

def compare_products(old_products, new_products):
    """Compare old and new product lists"""
    old_urls = {p['url'] for p in old_products}
    new_urls = {p['url'] for p in new_products}
    
    added_urls = new_urls - old_urls
    removed_urls = old_urls - new_urls
    
    added = [p for p in new_products if p['url'] in added_urls]
    removed = [p for p in old_products if p['url'] in removed_urls]
    
    return {
        'added': added,
        'removed': removed,
        'total_old': len(old_products),
        'total_new': len(new_products)
    }

def update_json_file(products):
    """Update products_data.json"""
    with open('products_data.json', 'w', encoding='utf-8') as f:
        json.dump(products, f, ensure_ascii=False, indent=2)
    print("✓ Updated products_data.json")

def update_html_files(products):
    """Update products.html with latest product data"""
    try:
        with open('products.html', 'r', encoding='utf-8') as f:
            html = f.read()
        
        # Convert products to JavaScript array
        products_js = json.dumps(products, ensure_ascii=False, indent=12)
        
        # Replace products array (note: variable is called 'allProducts' in HTML)
        pattern = r'const allProducts = \[[\s\S]*?\];'
        replacement = f'const allProducts = {products_js};'
        updated_html = re.sub(pattern, replacement, html, count=1)
        
        with open('products.html', 'w', encoding='utf-8') as f:
            f.write(updated_html)
        
        print("✓ Updated products.html")
    except Exception as e:
        print(f"⚠️  Failed to update HTML: {e}")

def log_sync(diff):
    """Log sync results"""
    log_entry = {
        'timestamp': datetime.now().isoformat(),
        'total_products': diff['total_new'],
        'added': len(diff['added']),
        'removed': len(diff['removed']),
        'added_products': [p['name'] for p in diff['added']],
        'removed_products': [p['name'] for p in diff['removed']]
    }
    
    try:
        with open('sync_log.json', 'r') as f:
            logs = json.load(f)
    except FileNotFoundError:
        logs = []
    
    logs.append(log_entry)
    logs = logs[-50:]
    
    with open('sync_log.json', 'w', encoding='utf-8') as f:
        json.dump(logs, f, ensure_ascii=False, indent=2)
    
    print("✓ Logged sync")

async def sync_products():
    """Main sync function"""
    print("\n" + "="*60)
    print("🔄 SYNCING PRODUCTS FROM T-SECONDHANDS.JP")
    print("="*60 + "\n")
    
    new_products = await fetch_latest_products()
    
    try:
        with open('products_data.json', 'r', encoding='utf-8') as f:
            old_products = json.load(f)
    except FileNotFoundError:
        old_products = []
    
    diff = compare_products(old_products, new_products)
    
    print("\n" + "="*60)
    print("📊 SYNC REPORT")
    print("="*60)
    print(f"   Old: {diff['total_old']} | New: {diff['total_new']}")
    print(f"   ➕ Added: {len(diff['added'])}")
    print(f"   ➖ Removed: {len(diff['removed'])}")
    
    if diff['added']:
        print(f"\n✨ NEW:")
        for p in diff['added'][:10]:
            print(f"   • {p['name']}")
    
    if diff['removed']:
        print(f"\n🗑️  REMOVED:")
        for p in diff['removed'][:10]:
            print(f"   • {p['name']}")
    
    if diff['added'] or diff['removed']:
        print(f"\n💾 Updating files...")
        update_json_file(new_products)
        update_html_files(new_products)
        log_sync(diff)
        print("\n✅ SYNC COMPLETED")
        return True
    else:
        print("\n✅ NO CHANGES")
        return False

if __name__ == '__main__':
    changed = asyncio.run(sync_products())
    exit(0)
