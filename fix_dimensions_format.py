#!/usr/bin/env python3
"""
Improve dimensions display format with better readability.
Add line breaks between each dimension for clearer presentation.
"""

import json

def format_dimensions_readable(product):
    """Create well-formatted dimensions text with line breaks"""
    dims = product.get('dimensions', {})
    
    if not dims:
        return {"height": "", "width": "", "depth": ""}
    
    height = dims.get('height', '')
    width = dims.get('width', '')
    depth = dims.get('depth', '')
    
    # Build the formatted text with line breaks
    parts = []
    if height:
        parts.append(f"Height in cm: approx. {height}")
    if width:
        parts.append(f"Width: approx. {width}")
    if depth:
        parts.append(f"Depth: approx. {depth}")
    
    # Join with newlines for better readability
    full_text = '\n'.join(parts)
    
    return {
        "height": "",
        "width": "",
        "depth": full_text if full_text else ""
    }

def main():
    print("📏 Improving dimensions display format...")
    
    # Load products
    with open('products_data.json', 'r', encoding='utf-8') as f:
        products = json.load(f)
    
    total = len(products)
    updated_count = 0
    
    for product in products:
        # Ensure detailText exists
        if 'detailText' not in product:
            product['detailText'] = {}
        
        # Format and update dimensions
        formatted_dims = format_dimensions_readable(product)
        product['detailText']['dimensions'] = formatted_dims
        
        if formatted_dims['depth']:  # If we have dimensions
            updated_count += 1
            print(f"  ✓ Updated: {product.get('name', 'Unknown')[:60]}")
    
    # Save updated data
    with open('products_data.json', 'w', encoding='utf-8') as f:
        json.dump(products, f, ensure_ascii=False, indent=2)
    
    print(f"\n✅ Complete!")
    print(f"   Total products: {total}")
    print(f"   Updated with dimensions: {updated_count}")
    print(f"\n💾 Saved to products_data.json")

if __name__ == '__main__':
    main()
