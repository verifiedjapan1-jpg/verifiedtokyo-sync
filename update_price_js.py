import glob
files = glob.glob('*.html')
for f in files:
    with open(f, 'r') as file:
        content = file.read()
    
    # In products.html and index.html
    if '`<div class="product-price">$' in content:
        # We need to replace the hardcoded price formatting with formatPrice(product.price)
        content = content.replace(
            '`<div class="product-price sold-out-price">$${Math.ceil(product.price)}</div><div style="font-size:13px;color:#999;font-weight:600;">SOLD OUT</div>`',
            '`<div class="product-price sold-out-price">${formatPrice(product.price)}</div><div style="font-size:13px;color:#999;font-weight:600;" data-i18n="SOLD OUT">SOLD OUT</div>`'
        )
        content = content.replace(
            '`<div class="product-price">$${Math.ceil(product.price)}</div>`',
            '`<div class="product-price">${formatPrice(product.price)}</div>`'
        )
    
    # In product-detail.html
    if "document.getElementById('product-price').textContent = `$${Math.ceil(product.price)}`;" in content:
        content = content.replace(
            "document.getElementById('product-price').textContent = `$${Math.ceil(product.price)}`;",
            "document.getElementById('product-price').textContent = formatPrice(product.price);"
        )
        
    with open(f, 'w') as file:
        file.write(content)
print("Updated JS rendering in HTML files!")
