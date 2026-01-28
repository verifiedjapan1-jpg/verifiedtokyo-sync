#!/usr/bin/env python3
"""Test script to verify image scraping for a single product"""

import asyncio
import time
from playwright.async_api import async_playwright

async def test_image_scraping():
    url = "https://t-secondhands.jp/products/armani-%E3%83%91%E3%83%BC%E3%83%97%E3%83%AB%E3%83%AC%E3%82%B6%E3%83%BC-%E3%83%8F%E3%83%B3%E3%83%89%E3%83%90%E3%83%83%E3%82%B0-%E3%83%95%E3%83%A9%E3%83%83%E3%83%97%E5%BC%8F-ar16"
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()
        
        print(f"🔗 Visiting: {url}")
        await page.goto(url, wait_until='networkidle', timeout=30000)
        await page.wait_for_timeout(2000)
        
        # Test thumbnail selector
        images = []
        thumbnails = await page.query_selector_all('.thumbnail img')
        print(f"✓ Found {len(thumbnails)} thumbnail elements")
        
        for thumb in thumbnails:
            src = await thumb.get_attribute('src')
            print(f"  - Found src: {src}")
            if src and ('cdn.shop' in src or 't-secondhands.jp' in src):
                # Handle protocol-relative URLs
                if src.startswith('//'):
                    src = 'https:' + src
                
                base_url = src.split('?')[0]
                full_url = f"{base_url}?v={int(time.time())}&width=1946"
                images.append(full_url)
                print(f"  ✓ Added: {full_url}")
        
        print(f"\n✅ Total images found: {len(images)}")
        
        await browser.close()
        return images

if __name__ == '__main__':
    result = asyncio.run(test_image_scraping())
    print(f"\nFinal result: {len(result)} images")
