#!/usr/bin/env python3
"""
Completely clean products_data.json by removing ALL literal newlines
from all string fields
"""
import json
import re

# Load products  
with open('products_data.json', 'r', encoding='utf-8') as f:
    products = json.load(f)

print(f"Cleaning {len(products)} products...\n")

def clean_string(s):
    """Remove literal newlines from string"""
    if not isinstance(s, str):
        return s
    # Replace literal newlines with spaces
    cleaned = s.replace('\n', ' ').replace('\r', '')
    # Remove multiple spaces
    cleaned = re.sub(r'\s+', ' ', cleaned)
    return cleaned.strip()

def clean_dict(d):
    """Recursively clean all strings in dictionary"""
    if isinstance(d, dict):
        return {k: clean_dict(v) for k, v in d.items()}
    elif isinstance(d, list):
        return [clean_dict(item) for item in d]
    elif isinstance(d, str):
        return clean_string(d)
    else:
        return d

# Clean all products
cleaned_products = [clean_dict(p) for p in products]

# Save cleaned data
with open('products_data.json', 'w', encoding='utf-8') as f:
    json.dump(cleaned_products, f, ensure_ascii=False, indent=2)

print(f"✅ Cleaned {len(products)} products")
print(f"💾 Saved to products_data.json")
print("\nNow run: python3 force_update_html.py")
