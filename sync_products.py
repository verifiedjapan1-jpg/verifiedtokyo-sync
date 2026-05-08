#!/usr/bin/env python3
"""
Auto-sync products from t-secondhands.jp via Shopify Collection API
"""
import json
import requests
from datetime import datetime
import re

BASE_URL = "https://t-secondhands.jp"

def html_to_text(html):
    if not html:
        return ''
    # ブロック要素の前後に改行を入れる
    html = re.sub(r'<br\s*/?>', '\n', html, flags=re.IGNORECASE)
    html = re.sub(r'<p[^>]*>', '\n', html, flags=re.IGNORECASE)
    html = re.sub(r'</p>', '\n', html, flags=re.IGNORECASE)
    html = re.sub(r'<li[^>]*>', '\n• ', html, flags=re.IGNORECASE)
    html = re.sub(r'</li>', '\n', html, flags=re.IGNORECASE)
    html = re.sub(r'<h[1-6][^>]*>', '\n', html, flags=re.IGNORECASE)
    html = re.sub(r'</h[1-6]>', '\n', html, flags=re.IGNORECASE)
    html = re.sub(r'<div[^>]*>', '\n', html, flags=re.IGNORECASE)
    html = re.sub(r'</div>', '\n', html, flags=re.IGNORECASE)
    # 残りのHTMLタグを除去
    html = re.sub(r'<[^>]+>', '', html)
    # HTMLエンティティを変換
    html = html.replace('&nbsp;', ' ').replace('&amp;', '&').replace('&lt;', '<').replace('&gt;', '>').replace('&#39;', "'").replace('&quot;', '"')
    # 連続する空行を整理
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
    all_products = []
    seen_handles = set()
    page = 1

    while True:
        url = f"{BASE_URL}/collections/all/products.json?limit=250&page={page}"
        print(f"📦 Fetching page {page}: {url}")

        try:
            r = requests.get(url, timeout=30, headers={'User-Agent': 'Mozilla/5.0'})
            data = r.json()
            products = data.get('products', [])

            if not products:
                print(f"✅ No more products at page {page}")
                break

            for p in products:
                handle = p['handle']
                if handle in seen_handles:
                    continue
                seen_handles.add(handle)

                variants = p.get('variants', [])
                variant = variants[0] if variants else {}
                price_jpy = float(variant.get('price', 0))
                price_usd = round(price_jpy / 155 + 200, 0)

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

            print(f"  Page {page}: {len(products)} products")
            page += 1

        except Exception as e:
            print(f"❌ Error on page {page}: {e}")
            break

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
