#!/usr/bin/env python3
import requests
from bs4 import BeautifulSoup
import json
import re
import time
from urllib.parse import urljoin, urlparse, parse_qs

def scrape_products():
    """Scrape all products from t-secondhands.jp with pagination"""
    base_url = "https://t-secondhands.jp"
    products_url = f"{base_url}/ja/collections/all"
    
    all_product_links = set()
    
    # Collect all product URLs from pages 1-8
    for page_num in range(1, 9):  # Pages 1 through 8
        url = f"{products_url}?page={page_num}"
        print(f"Fetching page {page_num}/8: {url}")
        
        try:
            response = requests.get(url, timeout=10)
            if response.status_code != 200:
                print(f"  Page {page_num} returned status {response.status_code}")
                continue
                
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find all product links on this page
            product_links_on_page = []
            for link in soup.find_all('a', href=True):
                if '/products/' in link['href'] and '/collections/' not in link['href']:
                    full_url = urljoin(base_url, link['href'])
                    # Remove query parameters
                    clean_url = full_url.split('?')[0]
                    product_links_on_page.append(clean_url)
            
            unique_new_links = set(product_links_on_page) - all_product_links
            all_product_links.update(unique_new_links)
            print(f"  Found {len(unique_new_links)} new products (total: {len(all_product_links)})")
            
            time.sleep(1)  # Be polite to server
            
        except Exception as e:
            print(f"Error fetching page {page_num}: {e}")
            continue
    
    print(f"\n✓ Found total of {len(all_product_links)} unique product URLs")
    
    # Scrape each product page
    products = []
    for idx, url in enumerate(sorted(all_product_links), 1):
        print(f"Scraping product {idx}/{len(all_product_links)}: {url.split('/')[-1][:50]}")
        
        try:
            time.sleep(0.5)  # Be polite
            response = requests.get(url, timeout=10)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract title
            title_tag = soup.find('h1', class_=re.compile('product|title')) or soup.find('h1')
            title = ""
            if title_tag:
                title = title_tag.get_text().strip()
                title = title.replace(' – T-Family', '').strip()
            
            if not title:
                title_meta = soup.find('meta', property='og:title')
                if title_meta:
                    title = title_meta.get('content', '').replace(' – T-Family', '').strip()
            
            # Extract brand (first word or from brand meta tag)
            brand = ""
            brand_meta = soup.find('meta', property='product:brand')
            if brand_meta:
                brand = brand_meta.get('content', '').strip()
            else:
                brand = title.split()[0] if title else "UNKNOWN"
            
            # Extract price
            price = 0
            price_meta = soup.find('met', property='product:price:amount')
            if price_meta:
                price_text = price_meta.get('content', '')
            else:
                # Try to find price in various ways
                price_tag = soup.find('span', class_=re.compile('price', re.I))
                if not price_tag:
                    price_tag = soup.find(string=re.compile('¥[\d,]+'))
                
                price_text = price_tag.get_text().strip() if hasattr(price_tag, 'get_text') else str(price_tag).strip() if price_tag else ""
            
            # Extract numeric value from price
            price_match = re.search(r'[\d,]+', price_text)
            if price_match:
                price = int(price_match.group(0).replace(',', ''))
            
            # Extract main image
            image_url = ""
            img_meta = soup.find('meta', property='og:image')
            if img_meta:
                image_url = img_meta.get('content', '')
            else:
                img_tag = soup.find('img', src=re.compile('cdn.*/products/|cdn.*/files/', re.I))
                if img_tag:
                    image_url = img_tag.get('src', '') or img_tag.get('data-src', '')
            
            if image_url and not image_url.startswith('http'):
                image_url = urljoin(base_url, image_url)
            
            # Clean up image URL (remove size parameters)
            image_url = re.sub(r'[?&]width=\d+', '', image_url)
            image_url = re.sub(r'[?&]v=\d+', '', image_url)
            
            # Extract product ID
            product_id = url.split('/')[-1]
            
            product = {
                'id': idx,
                'name': title or f"Product {idx}",
                'brand': brand.upper() if brand else "UNKNOWN",
                'price': price,
                'url': url,
                'imageUrl': image_url,
                'productId': product_id,
                'condition': 'good'  # Default
            }
            
            products.append(product)
            print(f"  ✓ {brand}: {title[:60]} - ¥{price:,}")
            
        except Exception as e:
            print(f"  ✗ Error scraping {url}: {e}")
            continue
    
    # Save to JSON
    output_file = 'products_data.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(products, f, ensure_ascii=False, indent=2)
    
    print(f"\n{'='*60}")
    print(f"✓ Successfully scraped {len(products)} products")
    print(f"✓ Data saved to {output_file}")
    print(f"{'='*60}")
    
    return products

if __name__ == '__main__':
    products = scrape_products()
