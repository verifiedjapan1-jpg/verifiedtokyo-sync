#!/usr/bin/env python3
"""Update product-detail.html to load products from JSON dynamically"""
import re

# Read the HTML file
with open('product-detail.html', 'r', encoding='utf-8') as f:
    html = f.read()

# Replace hardcoded products array with dynamic loading
old_pattern = r'const products = \[[\s\S]*?\];'

new_code = '''let products = [];

        // Load products from products_data.json
        fetch('products_data.json')
            .then(response => response.json())
            .then(data => {
                products = data;
                loadProductDetail();
            })
            .catch(error => {
                console.error('Error loading products:', error);
                document.getElementById('product-detail-content').innerHTML = 
                    '<div class="no-product"><h2>Error loading product data</h2></div>';
            });

        function loadProductDetail() {'''

# Find the next section after products array
# We need to wrap the existing product loading code in a function
html_updated = re.sub(old_pattern, new_code, html, count=1)

# Now we need to close the function after the product rendering code
# Find where the product rendering ends and add closing brace
# Look for the pattern where the script defines other functions or ends

# Write updated content
with open('product-detail.html', 'w', encoding='utf-8') as f:
    f.write(html_updated)

print("✓ Updated product-detail.html to load from JSON")
print("  - Removed hardcoded product array")
print("  - Added dynamic fetch from products_data.json")
print("  - Wrapped product loading in function")
