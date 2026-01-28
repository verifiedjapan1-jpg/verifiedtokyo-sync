#!/usr/bin/env python3
"""
Scrape multiple images for each product from t-secondhands.jp
"""
import requests
from bs4 import BeautifulSoup
import json
import time
import re

# Load existing product data
with open('products_data.json', 'r', encoding='utf-8') as f:
    products = json.load(f)

print(f"Loading product data for {len(products)} products...")

# Scrape additional images for each product
for idx, product in enumerate(products, 1):
    url = product['url']
    print(f"\n[{idx}/{len(products)}] Scraping images for: {product['name'][:50]}...")
    
    try:
        time.sleep(0.5)  # Be polite
        response = requests.get(url, timeout=10)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Find all product images
        images = []
        
        # Method 1: Look for image gallery
        gallery_images = soup.find_all('img', src=re.compile('cdn.*/files/'))
        for img in gallery_images:
            img_url = img.get('src') or img.get('data-src', '')
            if img_url and 'cdn' in img_url:
                # Clean up URL
                if not img_url.startswith('http'):
                    img_url = 'https://t-secondhands.jp' + img_url
                # Remove query parameters for cleaner URLs
                img_url = re.sub(r'\?.*$', '', img_url)
                if img_url not in images:
                    images.append(img_url)
        
        # Method 2: Look for srcset images
        srcset_imgs = soup.find_all('img', srcset=True)
        for img in srcset_imgs:
            srcset = img.get('srcset', '')
            # Extract URLs from srcset
            urls = re.findall(r'(https?://[^\s]+)', srcset)
            for url_item in urls:
                url_item = re.sub(r'\?.*$', '', url_item)
                if 'cdn' in url_item and url_item not in images:
                    images.append(url_item)
        
        # Store images (limit to first 6 for performance)
        product['images'] = images[:6] if images else [product['imageUrl']]
        print(f"  Found {len(product['images'])} images")
        
    except Exception as e:
        print(f"  Error: {e}")
        product['images'] = [product['imageUrl']]  # Fallback to main image

# Save updated data
with open('products_with_images.json', 'w', encoding='utf-8') as f:
    json.dump(products, f, ensure_ascii=False, indent=2)

print(f"\n✓ Saved product data with multiple images to products_with_images.json")
print(f"✓ Total products: {len(products)}")
