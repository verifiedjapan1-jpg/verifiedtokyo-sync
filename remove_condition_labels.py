#!/usr/bin/env python3
"""
Remove condition labels from products_data.json
"""

import json

# Read the product data
with open('products_data.json', 'r', encoding='utf-8') as f:
    products = json.load(f)

print(f"Processing {len(products)} products...")

# Remove condition fields from all products
for product in products:
    if 'condition' in product:
        del product['condition']
    if 'conditionText' in product:
        del product['conditionText']

# Write back to file
with open('products_data.json', 'w', encoding='utf-8') as f:
    json.dump(products, f, ensure_ascii=False, indent=2)

print(f"✅ Removed condition labels from {len(products)} products")
print("Updated products_data.json")
