#!/usr/bin/env python3
"""
Fix products.html by removing hardcoded product data and adding dynamic loading
"""
import re

# Read the file
with open('products.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Find the script section and replace the hardcoded data
# We need to find where the hardcoded array starts and ends
pattern = r'(<script>\s*//[^\n]*\s*let allProducts = \[\];)[^]*?(let currentProducts = \[\.\.\.allProducts\];)'

replacement = r'''<script>
        // All products data - loaded from JSON
        let allProducts = [];
        let currentProducts = [];

        // Load products from JSON file
        fetch('products_data.json')
            .then(response => response.json())
            .then(data => {
                allProducts = data;
                currentProducts = [...allProducts];
                console.log(`Loaded ${allProducts.length} products from JSON`);
                displayProducts(currentProducts);
                initFilters();
            })
            .catch(error => console.error('Error loading products:', error));'''

# Try to find and replace
updated_content = re.sub(pattern, replacement, content, flags=re.DOTALL)

# If that didn't work, try a different approach - find the products array more specifically
if updated_content == content:
    # Look for the array start to the currentProducts variable
    pattern2 = r'(let allProducts = \[\];)[^]*?(\/\/ Display products\s*function displayProducts)'
    
    replacement2 = r'''let allProducts = [];
        let currentProducts = [];

        // Load products from JSON file
        fetch('products_data.json')
            .then(response => response.json())
            .then(data => {
                allProducts = data;
                currentProducts = [...allProducts];
                console.log(`Loaded ${allProducts.length} products from JSON`);
                displayProducts(currentProducts);
                initFilters();
            })
            .catch(error => console.error('Error loading products:', error));

        // Display products
        function displayProducts'''
    
    updated_content = re.sub(pattern2, replacement2, content, flags=re.DOTALL)

# Write back
with open('products.html', 'w', encoding='utf-8') as f:
    f.write(updated_content)

print("✓ Fixed products.html - removed hardcoded data and added dynamic loading")
