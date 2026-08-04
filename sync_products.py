#!/usr/bin/env python3
"""
Auto-sync products from t-secondhands.jp via Shopify Collection API
Fetches ALL pages until no new products found
"""
import json
import requests
from datetime import datetime
import re

BASE_URL = "https://t-secondhands.jp"

def html_to_text(html):
    if not html:
        return ''
    html = re.sub(r'<br\s*/?>', '\n', html, flags=re.IGNORECASE)
    html = re.sub(r'<p[^>]*>', '\n', html, flags=re.IGNORECASE)
    html = re.sub(r'</p>', '\n', html, flags=re.IGNORECASE)
    html = re.sub(r'<li[^>]*>', '\n• ', html, flags=re.IGNORECASE)
    html = re.sub(r'</li>', '\n', html, flags=re.IGNORECASE)
    html = re.sub(r'<[^>]+>', '', html)
    html = html.replace('&nbsp;', ' ').replace('&amp;', '&').replace('&lt;', '<').replace('&gt;', '>').replace('&#39;', "'").replace('&quot;', '"')
    lines = [l.strip() for l in html.split('\n')]
    result = []
    prev_empty = False
    for line in lines:
        if not line:
            if not prev_empty:
                result.append('')
            prev_empty = True
        else:
            result.append(line)
            prev_empty = False
    return '\n'.join(result).strip()

def fetch_all_products():
    # Fetch live JPY to USD exchange rate
    try:
        req = requests.get('https://open.er-api.com/v6/latest/JPY', timeout=10)
        req.raise_for_status()
        USD_RATE = req.json()['rates']['USD']
        print(f"💱 Live Exchange Rate: 1 JPY = {USD_RATE} USD")
    except Exception as e:
        print(f"⚠️ Failed to fetch exchange rate, using default 1/155. Error: {e}")
        USD_RATE = 1 / 155

    all_products = []
    seen_handles = set()
    page = 1
    consecutive_no_new = 0  # Stop if 2 pages in a row have no new products

    while True:
        url = f"{BASE_URL}/collections/all/products.json?limit=250&page={page}"
        print(f"📦 Fetching page {page}: {url}")

        try:
            r = requests.get(url, timeout=60, headers={
                'User-Agent': 'Mozilla/5.0 (compatible; ProductSync/1.0)'
            })
            
            if r.status_code != 200:
                print(f"❌ HTTP {r.status_code} on page {page}. Stopping.")
                break

            data = r.json()
            products = data.get('products', [])

            if not products:
                print(f"✅ No products returned at page {page}. Done!")
                break

            new_on_this_page = 0
            for p in products:
                handle = p['handle']
                if handle in seen_handles:
                    continue
                seen_handles.add(handle)
                new_on_this_page += 1

                variants = p.get('variants', [])
                variant = variants[0] if variants else {}
                price_jpy = float(variant.get('price', 0))
                # T-Family USD price + $300 markup
                price_usd = round(price_jpy * USD_RATE + 300, 0)

                available = any(v.get('available', False) for v in variants)

                images = [img['src'] for img in p.get('images', [])]
                image_url = images[0] if images else ''

                title = p.get('title', '').replace(' - T-Family', '').strip()
                brand = title.split()[0].upper() if title else 'UNKNOWN'

                description = html_to_text(p.get('body_html', ''))

                product = {
                    'id': len(all_products) + 1,
                    'name': title,
                    'brand': brand,
                    'price': price_usd,
                    'available': available,
                    'url': f"{BASE_URL}/ja/products/{handle}",
                    'imageUrl': image_url,
                    'images': images,
                    'productId': handle,
                    'description': description,
                }
                all_products.append(product)

            print(f"  Page {page}: {len(products)} fetched, {new_on_this_page} new (total: {len(all_products)})")

            if new_on_this_page == 0:
                consecutive_no_new += 1
                print(f"  ⚠️ No new products on this page ({consecutive_no_new}/2)")
                if consecutive_no_new >= 2:
                    print("✅ Stopping: 2 consecutive pages with no new products")
                    break
            else:
                consecutive_no_new = 0

            page += 1

        except Exception as e:
            print(f"❌ Error on page {page}: {e}")
            # Try to continue on error
            page += 1
            if page > 20:  # Safety limit
                break
            continue

    available_count = sum(1 for p in all_products if p['available'])
    print(f"\n🎯 Total: {len(all_products)} (Available: {available_count}, Sold out: {len(all_products) - available_count})")
    return all_products

def main():
    print("\n" + "="*60)
    print("🔄 SYNCING PRODUCTS FROM T-SECONDHANDS.JP")
    print("="*60 + "\n")

    products = fetch_all_products()

    if not products:
        print("❌ No products fetched!")
        exit(1)

    with open('products_data.json', 'w', encoding='utf-8') as f:
        json.dump(products, f, ensure_ascii=False, indent=2)
    print(f"✅ Saved {len(products)} products to products_data.json")

    log_entry = {
        'timestamp': datetime.now().isoformat(),
        'total_products': len(products),
        'available': sum(1 for p in products if p['available']),
    }
    try:
        with open('sync_log.json', 'r', encoding='utf-8') as f:
            logs = json.load(f)
    except:
        logs = []
    logs.append(log_entry)
    with open('sync_log.json', 'w', encoding='utf-8') as f:
        json.dump(logs[-50:], f, ensure_ascii=False, indent=2)

    print("\n✅ SYNC COMPLETED")

if __name__ == '__main__':
    main()
