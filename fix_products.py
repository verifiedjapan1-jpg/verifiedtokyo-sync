#!/usr/bin/env python3
"""Fix products.html by properly inserting the product data"""
import json

# Load product data
with open('products_for_html.json', 'r', encoding='utf-8') as f:
    products = json.load(f)

# Rename imageUrl to image for all products
for p in products:
    p['image'] = p.pop('imageUrl')

# Read the original file
with open('products.html', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Find where to insert the products array
output_lines = []
in_products_section = False
products_done = False

for i, line in enumerate(lines):
    # Keep lines until we reach the products array
    if 'const products = [' in line and not products_done:
        output_lines.append('        // Product Data - 120 real products from t-secondhands.jp\n')
        output_lines.append('        const products = ' + json.dumps(products, ensure_ascii=False, indent=12) + ';\n')
        output_lines.append('\n')
        in_products_section = True
        products_done = True
        continue
    
    # Skip old product data
    if in_products_section:
        if 'let filteredProducts = [...products];' in line:
            in_products_section = False
            output_lines.append(line)
        continue
    
    output_lines.append(line)

# Write the fixed file
with open('products.html', 'w', encoding='utf-8') as f:
    f.writelines(output_lines)

print('✓ products.html fixed successfully')
print(f'✓ Total products: {len(products)}')
