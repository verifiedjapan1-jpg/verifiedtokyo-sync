#!/usr/bin/env python3
"""
Convert products_data.json to a JavaScript file to bypass CORS restrictions
when opening pages with file:// protocol.
"""

import json

def main():
    print("🔄 Converting JSON to JavaScript...")
    
    # Load products data
    with open('products_data.json', 'r', encoding='utf-8') as f:
        products = json.load(f)
    
    # Create JavaScript file with global variable
    js_content = f"""// Auto-generated from products_data.json
// This file allows the product data to be loaded without CORS issues on file:// protocol

const productsData = {json.dumps(products, ensure_ascii=False, indent=2)};
"""
    
    # Write JavaScript file
    with open('products_data.js', 'w', encoding='utf-8') as f:
        f.write(js_content)
    
    print(f"✅ Created products_data.js")
    print(f"   Products: {len(products)}")
    print(f"\n📝 Next: Update product-detail.html to use <script src=\"products_data.js\"></script>")

if __name__ == '__main__':
    main()
