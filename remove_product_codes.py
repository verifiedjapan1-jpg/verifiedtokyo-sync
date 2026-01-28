#!/usr/bin/env python3
"""
Remove product codes (e.g., AR16, Ba33, CH1992) from product names
"""
import json
import re

# Load products
with open('products_data.json', 'r', encoding='utf-8') as f:
    products = json.load(f)

print(f"Processing {len(products)} products...\n")

# Remove product codes from names
for product in products:
    original_name = product['name']
    
    # Pattern: Remove space + alphanumeric code at the end
    # Examples: " AR16", " Ba33", " CH1992", " BO26", " GU518", " LO2149"
    # Pattern matches: space + (uppercase letters + optional lowercase + numbers)
    cleaned_name = re.sub(r'\s+[A-Z]{1,2}[a-z]?\d+$', '', original_name)
    
    if cleaned_name != original_name:
        product['name'] = cleaned_name
        print(f"✓ {original_name}")
        print(f"  → {cleaned_name}\n")

# Save updated data
with open('products_data.json', 'w', encoding='utf-8') as f:
    json.dump(products, f, ensure_ascii=False, indent=2)

print(f"\n✅ Updated {len(products)} products")
print(f"💾 Saved to products_data.json")
