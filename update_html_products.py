#!/usr/bin/env python3
"""Update products.html with latest product data from products_data.json"""

import json
import re

# Load latest products
with open('products_data.json', 'r', encoding='utf-8') as f:
    products = json.load(f)

print(f"📦 Loaded {len(products)} products from JSON")

# Read products.html
with open('products.html', 'r', encoding='utf-8') as f:
    html = f.read()

# Convert products to JavaScript array format
products_js = json.dumps(products, ensure_ascii=False, indent=12)

# Find and replace the products array in products.html
pattern = r'const products = \[[\s\S]*?\];'
replacement = f'const products = {products_js};'

# Replace
updated_html = re.sub(pattern, replacement, html, count=1)

# Write back
with open('products.html', 'w', encoding='utf-8') as f:
    f.write(updated_html)

print(f"✅ Updated products.html with {len(products)} products")
