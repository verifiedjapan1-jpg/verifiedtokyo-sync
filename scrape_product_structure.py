#!/usr/bin/env python3
"""
Scrape one product detail page from t-secondhands.jp to understand the structure
and rebuild our product-detail.html with all the original features
"""
import asyncio
import json
from playwright.async_api import async_playwright

async def scrape_product_detail():
    """Scrape a single product detail page to understand structure"""
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        # Use the BALENCIAGA product as an example
        url = 'https://t-secondhands.jp/ja/products/balenciaga-%E9%BB%92-%E3%83%8A%E3%82%A4%E3%83%AD%E3%83%B3%E3%83%8F%E3%83%B3%E3%83%89%E3%83%90%E3%83%83%E3%82%B0-ba33'
        
        print(f"Scraping: {url}")
        await page.goto(url, wait_until='networkidle', timeout=30000)
        await asyncio.sleep(3)
        
        # Extract all images
        images = await page.evaluate('''
            () => {
                const imgElements = document.querySelectorAll('img[src*="cdn"]');
                return Array.from(imgElements).map(img => img.src).filter(src => src.includes('shop/files'));
            }
        ''')
        
        # Extract product info
        product_info = await page.evaluate('''
            () => {
                const title = document.querySelector('h1')?.textContent?.trim() || '';
                const priceEl = document.querySelector('.price, .product-price, [class*="price"]');
                const priceText = priceEl?.textContent?.trim() || '';
                
                // Get all text content
                const bodyText = document.body.innerText;
                
                return {
                    title: title,
                    priceText: priceText,
                    bodySnippet: bodyText.substring(0, 500)
                };
            }
        ''')
        
        await browser.close()
        
        return {
            'images': images,
            'info': product_info
        }

async def main():
    data = await scrape_product_detail()
    print("\n" + "="*60)
    print("PRODUCT DETAIL STRUCTURE")
    print("="*60)
    print(f"\nTitle: {data['info']['title']}")
    print(f"Price: {data['info']['priceText']}")
    print(f"\nImages found: {len(data['images'])}")
    for i, img in enumerate(data['images'][:5], 1):
        print(f"  {i}. {img[:80]}...")
    
    print(f"\nBody snippet:\n{data['info']['bodySnippet']}")
    
    # Save to file for reference
    with open('scraped_product_structure.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print("\n✓ Saved to scraped_product_structure.json")

if __name__ == '__main__':
    asyncio.run(main())
