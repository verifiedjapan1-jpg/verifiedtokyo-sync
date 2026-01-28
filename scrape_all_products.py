#!/usr/bin/env python3
"""
Scrape all 120 products from t-secondhands.jp using Playwright
"""
import asyncio
import json
import re
from playwright.async_api import async_playwright

async def scrape_all_products():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        print("Opening products page...")
        await page.goto('https://t-secondhands.jp/ja/collections/all', wait_until='networkidle')
        
        print("Scrolling to load all products...")
        # Scroll to bottom multiple times to trigger lazy loading
        for i in range(20):
            await page.evaluate('window.scrollTo(0, document.body.scrollHeight)')
            await asyncio.sleep(1)
            print(f"  Scroll {i+1}/20")
        
        print("\nExtracting product data...")
        products_data = await page.evaluate('''
            () => {
                const products = [];
                const productLinks = document.querySelectorAll('a[href*="/products/"]');
                const seen = new Set();
                
                productLinks.forEach((link) => {
                    const url = link.href;
                    if (url.includes('/products/') && !url.includes('/collections/') && !seen.has(url)) {
                        seen.add(url);
                        
                        let productCard = link.closest('.grid-item, .product-item, .product-card, [class*="product"]');
                        if (!productCard) productCard = link.parentElement;
                        
                        const img = productCard?.querySelector('img') || link.querySelector('img');
                        const titleEl = productCard?.querySelector('.product-title, .grid-product__title, h2, h3') || link.querySelector('.product-title, .grid-product__title, h2, h3');
                        const priceEl = productCard?.querySelector('.price, .product-price, [class*="price"]') || link.querySelector('.price, .product-price, [class*="price"]');
                        
                        const title = titleEl?.textContent?.trim() || link.getAttribute('title') || '';
                        const imageUrl = img?.src || img?.dataset?.src || '';
                        const price = priceEl?.textContent?.trim() || '';
                        
                        products.push({
                            name: title,
                            url: url,
                            imageUrl: imageUrl,
                            priceText: price
                        });
                    }
                });
                
                return products;
            }
        ''')
        
        print(f"\nFound {len(products_data)} unique product URLs")
        
        # Now scrape each product page for detailed info
        all_products = []
        for idx, prod in enumerate(products_data, 1):
            print(f"Scraping {idx}/{len(products_data)}: {prod['url'].split('/')[-1][:50]}")
            
            try:
                await page.goto(prod['url'], wait_until='networkidle', timeout=10000)
                
                # Extract detailed product info
                product_details = await page.evaluate('''
                    () => {
                        const title = document.querySelector('h1')?.textContent?.trim() || '';
                        const priceEl = document.querySelector('.price, .product-price, [class*="price"]');
                        const priceText = priceEl?.textContent?.trim() || '';
                        const priceMatch = priceText.match(/[\d,]+/);
                        const price = priceMatch ? parseInt(priceMatch[0].replace(/,/g, '')) : 0;
                        
                        const imgEl = document.querySelector('img[src*="cdn"], img[src*="products"]');
                        const imageUrl = imgEl?.src || '';
                        
                        return {
                            title: title.replace(' – T-Family', '').trim(),
                            price: price,
                            imageUrl: imageUrl
                        };
                    }
                ''')
                
                # Extract brand from title
                brand = product_details['title'].split()[0] if product_details['title'] else 'UNKNOWN'
                
                product = {
                    'id': idx,
                    'name': product_details['title'] or prod['name'],
                    'brand': brand.upper(),
                    'price': product_details['price'],
                    'url': prod['url'],
                    'imageUrl': product_details['imageUrl'] or prod['imageUrl'],
                    'productId': prod['url'].split('/')[-1],
                    'condition': 'good'
                }
                
                all_products.append(product)
                print(f"  ✓ {brand}: {product['name'][:60]} - ¥{product['price']:,}")
                
            except Exception as e:
                print(f"  ✗ Error: {e}")
                continue
        
        await browser.close()
        
        # Save to JSON
        with open('products_data_full.json', 'w', encoding='utf-8') as f:
            json.dump(all_products, f, ensure_ascii=False, indent=2)
        
        print(f"\n{'='*60}")
        print(f"✓ Successfully scraped {len(all_products)} products")
        print(f"✓ Data saved to products_data_full.json")
        print(f"{'='*60}")
        
        return all_products

if __name__ == '__main__':
    asyncio.run(scrape_all_products())
