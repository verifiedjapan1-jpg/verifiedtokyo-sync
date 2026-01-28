#!/usr/bin/env python3
"""
Recreate a minimal working product-detail.html that loads from products_data.json
This is a complete rebuild since the file was corrupted
"""

html_content = '''<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Product Details - Verified Tokyo</title>
    <link rel="stylesheet" href="styles.css">
    <script src="currency-converter.js"></script>
    <style>
        .product-detail-container {
            max-width: 1200px;
            margin: 100px auto 60px;
            padding: 0 40px;
        }
        
        .product-detail-image img {
            width: 100%;
            max-width: 600px;
            border-radius: 12px;
        }
        
        .product-detail-info {
            padding: 20px;
        }
        
        .product-detail-title {
            font-size: 32px;
            font-weight: 700;
            margin-bottom: 15px;
        }
        
        .product-detail-price {
            font-size: 48px;
            font-weight: 700;
            color: #1a1a1a;
            margin: 20px 0;
        }
        
        .no-product {
            text-align: center;
            padding: 100px 20px;
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
                    <li><a href="products.html">Products</a></li>
                    <li><a href="shopping-guide.html">Shopping Guide</a></li>
                    <li><a href="contact.html">Contact</a></li>
                </ul>
            </nav>
        </div>
    </header>

    <div id="product-detail-content">
        <div class="no-product"><h2>Loading product...</h2></div>
    </div>

    <footer style="background: white; padding: 60px 0; border-top: 1px solid #e5e5e5;">
        <div style="max-width: 1200px; margin: 0 auto; padding: 0 20px; text-align: center;">
            <p style="font-size: 14px; color: #666;">&copy; 2026 Verified Tokyo. All rights reserved.</p>
        </div>
    </footer>

    <script>
        let products = [];

        // Load products from products_data.json
        fetch('products_data.json')
            .then(response => response.json())
            .then(data => {
                products = data;
                console.log(`Loaded ${products.length} products`);
                loadProductDetail();
            })
            .catch(error => {
                console.error('Error loading products:', error);
                document.getElementById('product-detail-content').innerHTML = 
                    '<div class="no-product"><h2>Error loading product data</h2></div>';
            });

        function loadProductDetail() {
            // Get product ID from URL parameter
            const urlParams = new URLSearchParams(window.location.search);
            const productId = parseInt(urlParams.get('id'));
            
            console.log(`Looking for product ID: ${productId}`);

            // Find product by ID
            const product = products.find(p => p.id === productId);

            // Render product detail
            const contentDiv = document.getElementById('product-detail-content');

            if (product) {
                console.log(`Found product: ${product.name}`);
                
                contentDiv.innerHTML = `
                    <div class="product-detail-container">
                        <div class="product-detail-image">
                            <img src="${product.imageUrl}" alt="${product.name}">
                        </div>
                        <div class="product-detail-info">
                            <div class="product-brand" style="font-size: 14px; color: #666; text-transform: uppercase; letter-spacing: 1px;">${product.brand}</div>
                            <h1 class="product-detail-title">${product.name}</h1>
                            <div class="product-detail-price">${formatUSD(product.price)}</div>
                            <div class="product-condition" style="margin: 20px 0; padding: 15px; background: #f8f8f8; border-radius: 8px;">
                                <strong>Condition:</strong> ${product.conditionText || 'Good'}
                            </div>
                            <div style="margin: 30px 0;">
                                <a href="${product.url}" target="_blank" 
                                   class="offer-button" 
                                   style="display: inline-block; padding: 18px 50px; background: #1a1a1a; color: white; text-decoration: none; border-radius: 6px; font-weight: 700;">
                                    VIEW ON ORIGINAL SITE
                                </a>
                            </div>
                            <div style="margin-top: 30px;">
                                <a href="products.html" style="color: #666; text-decoration: none;">&larr; Back to Products</a>
                            </div>
                        </div>
                    </div>
                `;
            } else {
                console.log(`Product ID ${productId} not found`);
                contentDiv.innerHTML = `
                    <div class="no-product">
                        <h2>Product Not Found</h2>
                        <p>The product you're looking for doesn't exist.</p>
                        <a href="products.html" style="display: inline-block; margin-top: 20px; padding: 12px 30px; background: #1a1a1a; color: white; text-decoration: none; border-radius: 6px;">
                            Browse All Products
                        </a>
                    </div>
                `;
            }
        }
    </script>
</body>
</html>
'''

with open('product-detail.html', 'w', encoding='utf-8') as f:
    f.write(html_content)

print("✓ Recreated product-detail.html")
print("  - Loads products from products_data.json")
print("  - Simple, clean design")  
print("  - Correct ID matching")
