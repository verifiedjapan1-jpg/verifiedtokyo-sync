#!/usr/bin/env python3
"""
Fix USD prices by converting from priceJPY field
"""
import json

def main():
    print("\n" + "="*60)
    print("💱 FIXING USD PRICES FROM JPY")
    print("="*60 + "\n")
    
    # Standard exchange rate: 1 USD = 150 JPY
    exchange_rate = 1 / 150  # 1 JPY = 0.00667 USD
    
    # Load products
    with open('products_data.json', 'r', encoding='utf-8') as f:
        products = json.load(f)
    
    print(f"📦 Loaded {len(products)} products")
    
    # Fix prices
    fixed_count = 0
    for product in products:
        if 'priceJPY' in product:
            jpy_price = product['priceJPY']
            usd_price = round(jpy_price * exchange_rate)
            product['price'] = usd_price
            fixed_count += 1
    
    print(f"✓ Fixed {fixed_count} products")
    print(f"  Price range: ${min(p['price'] for p in products)} - ${max(p['price'] for p in products)}")
    
    # Save
    with open('products_data.json', 'w', encoding='utf-8') as f:
        json.dump(products, f, ensure_ascii=False, indent=2)
    
    print(f"\n✅ Saved to products_data.json")
    
    # Now rebuild products.html
    print("\n🔨 Rebuilding products.html...")
    import subprocess
    result = subprocess.run(['python3', 'rebuild_products_page.py'], 
                          capture_output=True, text=True)
    print(result.stdout)
    
    if result.returncode == 0:
        print("✅ All done!")
    else:
        print("⚠️  Warning: rebuild_products_page.py had issues")

if __name__ == '__main__':
    main()
