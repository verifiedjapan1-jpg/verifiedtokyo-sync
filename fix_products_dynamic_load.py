#!/usr/bin/env python3
"""
Convert products.html to load data dynamically from products_data.json
"""
import re

# Read current HTML
with open('products.html', 'r', encoding='utf-8') as f:
    html = f.read()

# Replace the embedded products array with dynamic fetch
# Find the pattern: const allProducts = [{...}];
pattern = r'const allProducts = \[[\s\S]*?\];'

replacement = '''const allProducts = [];

        // Load products from JSON file
        fetch('products_data.json')
            .then(response => response.json())
            .then(data => {
                allProducts.push(...data);
                currentProducts = [...allProducts];
                console.log(`Loaded ${allProducts.length} products`);
                displayProducts(currentProducts);
                initFilters();
            })
            .catch(error => console.error('Error loading products:', error));'''

# Make the replacement
updated_html = re.sub(pattern, replacement, html, count=1)

# Also need to remove the initial displayProducts call since it will be called after fetch
updated_html = re.sub(
    r'document\.addEventListener\(\'DOMContentLoaded\',.*?\}\);',
    '// Products will be loaded via fetch above',
    updated_html,
    flags=re.DOTALL
)

# Write back
with open('products.html', 'w', encoding='utf-8') as f:
    f.write(updated_html)

print("✅ Updated products.html to load data dyn_file_async from products_data.json")
print("   This ensures the page always shows the latest USD prices")
