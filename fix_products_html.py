#!/usr/bin/env python3
"""
Revert products.html to working state by removing the broken const products array
and letting JavaScript load from products_data.json instead
"""

import re

# Read broken HTML
with open('products.html', 'r', encoding='utf-8') as f:
    html = f.read()

# Remove the broken products array and replace with empty array
# The page should load products from products_data.json via fetch
pattern = r'const products = \[[\s\S]*?\];'
replacement = '''const products = [];
        
        // Load products from JSON file
        fetch('products_data.json')
            .then(response => response.json())
            .then(data => {
                products.push(...data);
                displayProducts(currentProducts);
                console.log(`Loaded ${products.length} products from JSON`);
            })
            .catch(error => console.error('Error loading products:', error));'''

updated_html = re.sub(pattern, replacement, html, count=1)

# Write back
with open('products.html', 'w', encoding='utf-8') as f:
    f.write(updated_html)

print("✅ products.htmlを修正しました - JSONから動的にロードするようになりました")
