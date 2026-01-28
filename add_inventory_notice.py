#!/usr/bin/env python3
"""
Add inventory notice to all products' detailText.intro field.
"""

import json

def main():
    print("📝 Adding inventory notice to all products...")
    
    # The standard notice text
    notice_text = """We update our inventory daily,
There may be sold items listed.
Thank you for your understanding."""
    
    # Load products
    with open('products_data.json', 'r', encoding='utf-8') as f:
        products = json.load(f)
    
    total = len(products)
    updated_count = 0
    
    for product in products:
        # Ensure detailText exists
        if 'detailText' not in product:
            product['detailText'] = {}
        
        # Set the intro field
        product['detailText']['intro'] = notice_text
        updated_count += 1
        print(f"  ✓ Updated: {product.get('name', 'Unknown')[:60]}")
    
    # Save updated data
    with open('products_data.json', 'w', encoding='utf-8') as f:
        json.dump(products, f, ensure_ascii=False, indent=2)
    
    print(f"\n✅ Complete!")
    print(f"   Total products: {total}")
    print(f"   Updated: {updated_count}")
    print(f"\n💾 Saved to products_data.json")

if __name__ == '__main__':
    main()
