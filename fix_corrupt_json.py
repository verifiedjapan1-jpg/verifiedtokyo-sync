#!/usr/bin/env python3
"""
Clean up corrupted specifications in products_data.json
Remove embedded newlines and truncated values
"""
import json
import re

# Load products
with open('products_data.json', 'r', encoding='utf-8') as f:
    products = json.load(f)

print(f"Cleaning {len(products)} products...\n")

fixed_count = 0

for product in products:
    if 'specifications' in product and product['specifications']:
        specs = product['specifications']
        fixed_specs = False
        
        for key, value in specs.items():
            if value and isinstance(value, str):
                # Remove everything from newline onwards
                cleaned = value.split('\n')[0].strip()
                # Remove truncation markers
                cleaned = re.sub(r'\.{3,}$', '', cleaned)
                
                if cleaned != value:
                    specs[key] = cleaned
                    fixed_specs = True
        
        if fixed_specs:
            fixed_count += 1
            print(f"✓ Fixed: {product['name'][:50]}")

# Save cleaned data
with open('products_data.json', 'w', encoding='utf-8') as f:
    json.dump(products, f, ensure_ascii=False, indent=2)

print(f"\n✅ Fixed {fixed_count} products")
print(f"💾 Saved to products_data.json")
