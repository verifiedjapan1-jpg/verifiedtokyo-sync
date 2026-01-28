#!/usr/bin/env python3
"""
Scrape detailed product specifications from t-secondhands.jp
"""
import requests
from bs4 import BeautifulSoup
import json
import time
import re

# Load existing product data with images
with open('products_with_images.json', 'r', encoding='utf-8') as f:
    products = json.load(f)

print(f"Loading detailed specs for {len(products)} products...")

def extract_dimensions(text):
    """Extract height, width, depth from text"""
    dimensions = {}
    
    # Look for Height
    height_match = re.search(r'Height[:\s]*[Aa]pprox\.?\s*(\d+)\s*cm', text, re.IGNORECASE)
    if height_match:
        dimensions['height'] = height_match.group(1)
    
    # Look for Width
    width_match = re.search(r'Width[:\s]*[Aa]pprox\.?\s*(\d+)\s*cm', text, re.IGNORECASE)
    if width_match:
        dimensions['width'] = width_match.group(1)
    
    # Look for Depth
    depth_match = re.search(r'Depth[:\s]*[Aa]pprox\.?\s*(\d+)\s*cm', text, re.IGNORECASE)
    if depth_match:
        dimensions['depth'] = depth_match.group(1)
    
    return dimensions

def extract_specifications(text):
    """Extract color, material, etc from text"""
    specs = {}
    
    # Look for Color
    color_match = re.search(r'Color[:\s]*([^\n]+)', text, re.IGNORECASE)
    if color_match:
        specs['color'] = color_match.group(1).strip()
    
    # Look for Material
    material_match = re.search(r'Material[:\s]*([^\n]+)', text, re.IGNORECASE)
    if material_match:
        specs['material'] = material_match.group(1).strip()
    
    # Look for Design
    design_match = re.search(r'Design[:\s]*([^\n]+)', text, re.IGNORECASE)
    if design_match:
        specs['design'] = design_match.group(1).strip()
    
    # Look for Style
    style_match = re.search(r'Style[:\s]*([^\n]+)', text, re.IGNORECASE)
    if style_match:
        specs['style'] = style_match.group(1).strip()
    
    # Look for Features
    features_match = re.search(r'Features[:\s]*([^\n]+)', text, re.IGNORECASE)
    if features_match:
        specs['features'] = features_match.group(1).strip()
    
    return specs

# Scrape details for each product
for idx, product in enumerate(products, 1):
    url = product['url']
    print(f"\n[{idx}/{len(products)}] {product['name'][:50]}...")
    
    try:
        time.sleep(0.5)  # Be polite
        response = requests.get(url, timeout=10)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Get all text from the page
        page_text = soup.get_text()
        
        # Extract dimensions
        dimensions = extract_dimensions(page_text)
        if dimensions:
            product['dimensions'] = dimensions
            print(f"  Dimensions: {dimensions}")
        
        # Extract specifications
        specs = extract_specifications(page_text)
        if specs:
            product['specifications'] = specs
            print(f"  Specs: {list(specs.keys())}")
        
        # Extract description paragraphs
        description_parts = []
        
        # Find paragraphs that contain product details
        for p in soup.find_all('p'):
            text = p.get_text().strip()
            # Skip empty or very short paragraphs
            if len(text) > 20 and not text.startswith('http'):
                # Check if it looks like product description
                if any(keyword in text.lower() for keyword in ['bag', 'leather', 'material', 'design', 'condition']):
                    description_parts.append(text)
        
        if description_parts:
            product['detailedDescription'] = ' '.join(description_parts[:3])  # First 3 relevant paragraphs
        
    except Exception as e:
        print(f"  Error: {e}")

# Save updated data
with open('products_with_details.json', 'w', encoding='utf-8') as f:
    json.dump(products, f, ensure_ascii=False, indent=2)

print(f"\n✓ Saved detailed product data to products_with_details.json")
print(f"✓ Total products: {len(products)}")

# Print summary
products_with_dims = sum(1 for p in products if 'dimensions' in p)
products_with_specs = sum(1 for p in products if 'specifications' in p)
print(f"✓ Products with dimensions: {products_with_dims}")
print(f"✓ Products with specifications: {products_with_specs}")
