#!/usr/bin/env python3
"""
Convert all product prices from JPY to USD
"""
import json
import asyncio
from playwright.async_api import async_playwright

async def get_exchange_rate():
    """Get current JPY to USD exchange rate"""
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        try:
            # Use a reliable exchange rate API
            await page.goto('https://api.exchangerate-api.com/v4/latest/JPY', timeout=10000)
            content = await page.content()
            
            # Extract JSON from page
            import re
            match = re.search(r'\{.*\}', content)
            if match:
                data = json.loads(match.group())
                rate = data['rates']['USD']
                print(f"✓ Current exchange rate: 1 JPY = ${rate:.6f} USD")
                print(f"  (Approximately ${1/rate:.0f} JPY = $1 USD)")
                await browser.close()
                return rate
        except Exception as e:
            print(f"Failed to fetch rate: {e}")
        
        await browser.close()
        # Fallback rate (approximate)
        fallback_rate = 0.0067  # ~150 JPY = 1 USD
        print(f"⚠️  Using fallback rate: 1 JPY = ${fallback_rate} USD")
        return fallback_rate

def convert_prices_to_usd(products, exchange_rate):
    """Convert all product prices from JPY to USD"""
    converted = []
    for product in products:
        jpy_price = product['price']
        usd_price = round(jpy_price * exchange_rate)
        
        # Update product with USD price
        product_copy = product.copy()
        product_copy['price'] = usd_price
        product_copy['priceJPY'] = jpy_price  # Keep original for reference
        
        converted.append(product_copy)
    
    return converted

async def main():
    print("\n" + "="*60)
    print("💱 CONVERTING PRICES FROM JPY TO USD")
    print("="*60 + "\n")
    
    # Get exchange rate
    exchange_rate = await get_exchange_rate()
    
    # Load products
    with open('products_data.json', 'r', encoding='utf-8') as f:
        products = json.load(f)
    
    print(f"\n📦 Loaded {len(products)} products")
    print(f"   Price range (JPY): ¥{min(p['price'] for p in products):,} - ¥{max(p['price'] for p in products):,}")
    
    # Convert
    converted_products = convert_prices_to_usd(products, exchange_rate)
    
    print(f"   Price range (USD): ${min(p['price'] for p in converted_products):,} - ${max(p['price'] for p in converted_products):,}")
    
    # Save
    with open('products_data.json', 'w', encoding='utf-8') as f:
        json.dump(converted_products, f, ensure_ascii=False, indent=2)
    
    print(f"\n✅ Successfully converted {len(converted_products)} products to USD")
    print(f"   Saved to products_data.json")

if __name__ == '__main__':
    asyncio.run(main())
