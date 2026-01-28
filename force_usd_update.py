#!/usr/bin/env python3
"""
Force update products_data.json with new USD pricing
This will run the scraper again and force an update even if no product changes
"""
import asyncio
import sys

# Import the sync function
sys.path.insert(0, '/Users/rionaaigbe/.gemini/antigravity/playground/empty-orion/t-secondhands-site')
from sync_products import fetch_latest_products, update_json_file, update_html_files

async def force_update():
    print("\n" + "="*60)
    print("🔄 FORCE UPDATING PRODUCTS WITH USD PRICING")
    print("="*60 + "\n")
    
    # Fetch all products with new USD pricing
    products = await fetch_latest_products()
    
    # Force update both files
    update_json_file(products)
    update_html_files(products)
    
    print("\n✅ FORCE UPDATE COMPLETED")
    print(f"📦 Updated {len(products)} products with USD pricing\n")

if __name__ == '__main__':
    asyncio.run(force_update())
