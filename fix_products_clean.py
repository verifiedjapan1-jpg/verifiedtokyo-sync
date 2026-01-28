#!/usr/bin/env python3
"""
Fix products.html by removing all hardcoded product data
"""

# Read the file
with open('products.html', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Find the lines to keep
# Keep everything up to and including line 190 (the catch error line)
# Skip everything from 191 to 1776
# Keep everything from 1777 onwards (the displayProducts function)

# Line numbers are 1-indexed in the editor, but 0-indexed in Python lists
keep_start = lines[:190]  # Lines 1-190
keep_end = lines[1776:]   # Lines 1777 onwards

# Combine
new_content = keep_start + keep_end

# Write back
with open('products.html', 'w', encoding='utf-8') as f:
    f.writelines(new_content)

print("✓ Removed hardcoded product data (1586 lines)")
print("✓ Products will now load dynamically from products_data.json")
