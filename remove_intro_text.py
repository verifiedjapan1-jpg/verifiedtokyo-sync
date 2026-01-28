#!/usr/bin/env python3
"""
Remove intro text from all products' detailText.intro field.
Removes the common text about store availability and "Dimensions in cm"
"""

import json

def clean_intro_text(intro_text):
    """Remove unwanted intro text patterns"""
    if not intro_text:
        return ""
    
    # Split by newlines
    lines = intro_text.split('\\n')
    cleaned_lines = []
    
    # Skip lines that match unwanted patterns
    skip_patterns = [
        'Available in our physical store',
        'Available in physical store',
        'Available in-store',
        'We update inventory daily',
        'We update our inventory daily',
        'but please note that sold items',
        'but items may occasionally',
        'We appreciate your understanding',
        'Dimensions in cm',
        'Tax included',
        'Shipping calculated'
    ]
    
    for line in lines:
        line = line.strip()
        # Skip empty lines
        if not line:
            continue
        # Skip lines matching any skip pattern
        if any(pattern in line for pattern in skip_patterns):
            continue
        # Keep the line
        cleaned_lines.append(line)
    
    return '\\n'.join(cleaned_lines) if cleaned_lines else ""

def main():
    print("🧹 Removing intro text from all products...")
    
    # Load products
    with open('products_data.json', 'r', encoding='utf-8') as f:
        products = json.load(f)
    
    total = len(products)
    updated_count = 0
    
    for product in products:
        if 'detailText' in product and 'intro' in product['detailText']:
            original_intro = product['detailText']['intro']
            cleaned_intro = clean_intro_text(original_intro)
            
            if original_intro != cleaned_intro:
                product['detailText']['intro'] = cleaned_intro
                updated_count += 1
                print(f"  ✓ Updated: {product.get('name', 'Unknown')[:60]}")
    
    # Save updated data
    with open('products_data.json', 'w', encoding='utf-8') as f:
        json.dump(products, f, ensure_ascii=False, indent=2)
    
    print(f"\n✅ Complete!")
    print(f"   Total products: {total}")
    print(f"   Updated: {updated_count}")
    print(f"   Unchanged: {total - updated_count}")
    print(f"\n💾 Saved to products_data.json")

if __name__ == '__main__':
    main()
