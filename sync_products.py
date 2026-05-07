#!/usr/bin/env python3
"""
Auto-sync products from t-secondhands.jp via Shopify JSON API
"""
import json
import requests
from datetime import datetime

BASE_URL = "https://t-secondhands.jp"

def fetch_all_products():
    all_products = []
    seen_handles = set()
    page = 1

    while True:
        url = f"{BASE_URL}/products.json?limit=250&page={page}"
        print(f"📦 Fetching page {page}: {url}")

        try:
            r = requests.get(url, timeout=30, headers={'User-Agent': 'Mozilla/5.0'})
            data = r.json()
            products = data.get('products', [])

            if not products:
                print(f"✅ No more products at page {page}")
                break

            new_count = 0
            for p in products:
                handle = p['handle']

                # 重複スキップ
                if handle in seen_handles:
                    continue
                seen_handles.add(handle)

                # 在庫チェック：available=falseの商品をスキップ
                variants = p.get('variants', [])
                available = any(v.get('available', False) for v in variants)
                if not available:
                    continue

                new_count += 1

                variant = variants[0] if variants else {}
                price_jpy = float(variant.get('price', 0))
                price_usd = round(price_jpy / 155 + 200, 0)

                images = [img['src'] for img in p.get('images', [])]
                image_url = images[0] if images else ''

                title = p.get('title', '').replace(' - T-Family', '').strip()
                brand = title.split()[0].upper() if title else 'UNKNOWN'

                body_html = p.get('body_html', '')
                description = ''
                if body_html:
                    import re
                    description = re.sub('<[^>]+>', ' ', body_html).strip()
                    description = ' '.join(description.split())[:500]

                product = {
                    'id': len(all_products) + 1,
                    'name': title,
                    'brand': brand,
                    'price': price_usd,
                    'url': f"{BASE_URL}/ja/products/{handle}",
                    'imageUrl': image_url,
                    'images': images,
                    'productId': handle,
                    'description': description,
                }
                all_products.append(product)

            print(f"  Added {new_count} available products")

            if new_count == 0 and len(products) < 250:
                break

            page += 1

        except Exception as e:
            print(f"❌ Error on page {page}: {e}")
            break

    print(f"\n🎯 Total available products: {len(all_products)}")
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
