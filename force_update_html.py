#!/usr/bin/env python3
"""Force update products.html with correct data from products_data.json"""
import json
import re

# Read correct data from JSON
with open('products_data.json', 'r', encoding='utf-8') as f:
    products = json.load(f)

print(f"Loaded {len(products)} products from JSON")
print(f"First product price: {products[0]['price']}")

# Read HTML
with open('products.html', 'r', encoding='utf-8') as f:
    html = f.read()

# Convert products to JavaScript array
# Use json.dumps with proper escaping for HTML embedding
products_js = json.dumps(products, ensure_ascii=False, indent=8)

# No additional escaping needed - json.dumps handles it correctly
# Just make sure we're using the raw JSON string
pattern = r'const allProducts = \[[\s\S]*?\];'
replacement = f'const allProducts = {products_js};'
updated_html = re.sub(pattern, replacement, html, count=1)

# Write updated HTML
with open('products.html', 'w', encoding='utf-8') as f:
    f.write(updated_html)

print("✓ Force updated products.html")
print(f"Embedded {len(products)} products with correct prices")
