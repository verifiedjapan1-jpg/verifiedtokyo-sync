#!/usr/bin/env python3
"""
Rebuild products.html with proper JavaScript and USD prices
"""
import json

# Load USD-converted products
with open('products_data.json', 'r', encoding='utf-8') as f:
    products = json.load(f)

print(f"📦 Loaded {len(products)} products with USD prices")

# Create products.html HTML template
html_template = '''<!DOCTYPE html>
<html lang="en">

<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Products | Verified Tokyo | Secondhand Brand Bags Online Store</title>
    <meta name="description"
        content="Verified Tokyo's list of secondhand brand bags. We offer a wide selection of popular brand bags including LOUIS VUITTON, CHANEL, GUCCI, and HERMES.">
    <link rel="stylesheet" href="styles.css">
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link
        href="https://fonts.googleapis.com/css2?family=Noto+Serif+JP:wght@400;600;700&family=Noto+Sans+JP:wght@300;400;500;600&display=swap"
        rel="stylesheet">

    <style>
        /* Product grid styles */
        .products-container {
            max-width: 1400px;
            margin: 0 auto;
            padding: 20px;
        }

        .products-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
            gap: 30px;
            margin-top: 30px;
        }

        .product-card {
            border: 1px solid #e0e0e0;
            border-radius: 8px;
            overflow: hidden;
            cursor: pointer;
            transition: transform 0.3s, box-shadow 0.3s;
        }

        .product-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 5px 20px rgba(0,0,0,0.1);
        }

        .product-image {
            width: 100%;
            height: 300px;
            object-fit: cover;
        }

        .product-info {
            padding: 15px;
        }

        .product-brand {
            font-size: 12px;
            color: #666;
            text-transform: uppercase;
            letter-spacing: 1px;
        }

        .product-title {
            font-size: 16px;
            margin: 8px 0;
            color: #333;
        }

        .product-price {
            font-size: 20px;
            font-weight: 700;
            color: #000;
            margin-top: 10px;
        }

        .product-condition {
            font-size: 12px;
            color: #888;
            margin-top: 5px;
        }

        .filters {
            margin: 20px 0;
            display: flex;
            gap: 15px;
            flex-wrap: wrap;
        }

        .filter-select {
            padding: 10px 15px;
            border: 1px solid #ddd;
            border-radius: 5px;
            font-size: 14px;
        }
    </style>
</head>

<body>
    <header>
        <div class="header-container">
            <div class="logo-section">
                <a href="index.html" class="logo-link">
                    <h1 class="logo">Verified Tokyo</h1>
                    <p class="tagline">Premium Secondhand Luxury Bags</p>
                </a>
            </div>
            <nav>
                <ul class="nav-links">
                    <li><a href="index.html">Home</a></li>
                    <li><a href="products.html" class="active">Products</a></li>
                    <li><a href="shopping-guide.html">Shopping Guide</a></li>
                    <li><a href="contact.html">Contact</a></li>
                </ul>
            </nav>
            <div class="header-search">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                    <circle cx="11" cy="11" r="8"></circle>
                    <path d="m21 21-4.35-4.35"></path>
                </svg>
            </div>
        </div>
    </header>

    <div class="products-container">
        <h1>All Products</h1>
        <p id="product-count">Loading products...</p>
        
        <div class="filters">
            <select class="filter-select" id="brand-filter">
                <option value="">All Brands</option>
            </select>
            <select class="filter-select" id="sort-filter">
                <option value="default">Default</option>
                <option value="price-low">Price: Low to High</option>
                <option value="price-high">Price: High to Low</option>
                <option value="brand">Brand</option>
            </select>
        </div>

        <div class="products-grid" id="products-grid">
            <!-- Products will be inserted here -->
        </div>
    </div>

    <footer style="background: white; padding: 60px 0; border-top: 1px solid #e5e5e5;">
        <div style="max-width: 1200px; margin: 0 auto; padding: 0 20px;">
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 40px;">
                <div>
                    <h3 style="font-size: 18px; font-weight: 700; margin-bottom: 20px;">Verified Tokyo</h3>
                    <p style="color: #666; line-height: 1.6;">Premium secondhand luxury bags from Tokyo</p>
                </div>
                <div>
                    <h4 style="font-size: 14px; font-weight: 600; margin-bottom: 15px;">Quick Links</h4>
                    <ul style="list-style: none; padding: 0;">
                        <li style="margin-bottom: 10px;"><a href="index.html" style="color: #666; text-decoration: none;">Home</a></li>
                        <li style="margin-bottom: 10px;"><a href="products.html" style="color: #666; text-decoration: none;">Products</a></li>
                        <li style="margin-bottom: 10px;"><a href="shopping-guide.html" style="color: #666; text-decoration: none;">Shopping Guide</a></li>
                        <li style="margin-bottom: 10px;"><a href="contact.html" style="color: #666; text-decoration: none;">Contact</a></li>
                    </ul>
                </div>
                <div style="text-align: right;">
                    <img src="images/payment-methods.png" alt="Accepted Payment Methods" style="max-width: 300px; height: auto;">
                </div>
            </div>
            <div style="text-align: center; padding-top: 20px; border-top: 1px solid #e5e5e5; margin-top: 40px;">
                <p style="font-size: 14px; color: #666;">&copy; 2026 Verified Tokyo. All rights reserved.</p>
            </div>
        </div>
    </footer>

    <script>
        // All products data
        const allProducts = ''' + json.dumps(products, ensure_ascii=False, indent=4) + ''';

        let currentProducts = [...allProducts];

        // Display products
        function displayProducts(products) {
            const grid = document.getElementById('products-grid');
            const count = document.getElementById('product-count');
            
            count.textContent = `Total ${products.length} items`;
            
            grid.innerHTML = products.map(product => `
                <div class="product-card" onclick="window.location.href='product-detail.html?id=${product.id}'">
                    <img src="${product.imageUrl}" 
                         alt="${product.name}" 
                         class="product-image"
                         onerror="this.src='images/placeholder.jpg'">
                    <div class="product-info">
                        <div class="product-brand">${product.brand}</div>
                        <h3 class="product-title">${product.name}</h3>
                        <div class="product-condition">${product.conditionText}</div>
                        <div class="product-price">$${product.price}</div>
                    </div>
                </div>
            `).join('');
        }

        // Initialize filters
        function initFilters() {
            const brands = [...new Set(allProducts.map(p => p.brand))].sort();
            const brandFilter = document.getElementById('brand-filter');
            
            brands.forEach(brand => {
                const option = document.createElement('option');
                option.value = brand;
                option.textContent = brand;
                brandFilter.appendChild(option);
            });

            // Brand filter
            brandFilter.addEventListener('change', filterProducts);
            
            // Sort filter
            document.getElementById('sort-filter').addEventListener('change', sortProducts);
        }

        function filterProducts() {
            const brand = document.getElementById('brand-filter').value;
            
            currentProducts = brand 
                ? allProducts.filter(p => p.brand === brand)
                : [...allProducts];
            
            sortProducts();
        }

        function sortProducts() {
            const sort = document.getElementById('sort-filter').value;
            
            switch(sort) {
                case 'price-low':
                    currentProducts.sort((a, b) => a.price - b.price);
                    break;
                case 'price-high':
                    currentProducts.sort((a, b) => b.price - a.price);
                    break;
                case 'brand':
                    currentProducts.sort((a, b) => a.brand.localeCompare(b.brand));
                    break;
            }
            
            displayProducts(currentProducts);
        }

        // Initialize on page load
        document.addEventListener('DOMContentLoaded', () => {
            console.log(`Loaded ${allProducts.length} products`);
            displayProducts(currentProducts);
            initFilters();
        });
    </script>
</body>
</html>'''

# Write the file
with open('products.html', 'w', encoding='utf-8') as f:
    f.write(html_template)

print(f"✅ Created products.html with {len(products)} products")
print(f"   Price range: ${min(p['price'] for p in products)} - ${max(p['price'] for p in products)}")
