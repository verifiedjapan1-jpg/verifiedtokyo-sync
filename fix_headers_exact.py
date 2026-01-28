#!/usr/bin/env python3
"""Fix shopping-guide.html and contact.html headers to exactly match index.html"""

# Exact head section from index.html (lines 4-16)
INDEX_HEAD = '''    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Verified Tokyo | Secondhand Luxury Bags Store/secondhandshop/thriftstore</title>
    <meta name="description"
        content="Secondhand luxury bags store with international shipping available. Purchase popular brand bags like LOUIS VUITTON, CHANEL, PRADA at great prices.">
    <link rel="stylesheet" href="styles.css">
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link
        href="https://fonts.googleapis.com/css2?family=Noto+Serif+JP:wght@400;600;700&family=Noto+Sans+JP:wght@300;400;500;600&display=swap"
        rel="stylesheet">'''

# Exact header from index.html (lines 19-45)
INDEX_HEADER = '''    <!-- Header -->
    <header class="header">
        <div class="main-header">
            <div class="container">
                <div class="logo-nav-container">
                    <h1 class="logo">Verified Tokyo</h1>

                    <nav class="main-nav">
                        <a href="index.html" class="nav-link">Home</a>
                        <a href="products.html" class="nav-link">Products</a>
                        <a href="shopping-guide.html" class="nav-link">Shopping Guide</a>
                        <a href="contact.html" class="nav-link">Contact</a>
                    </nav>
                </div>

                <div class="search-container">
                    <div class="search-icon" onclick="window.location.href='products.html'">
                        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor"
                            stroke-width="2">
                            <circle cx="11" cy="11" r="8" />
                            <path d="M21 21l-4.35-4.35" />
                        </svg>
                    </div>
                </div>
            </div>
        </div>
    </header>'''

def fix_shopping_guide():
    """Fix shopping-guide.html"""
    with open('shopping-guide.html', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Replace head content
    head_start = content.find('<head>') + len('<head>\n')
    head_end = content.find('</head>')
    
    # Find where styles start (keep page-specific styles)
    style_start = content.find('<style>', head_start)
    
    new_head = INDEX_HEAD + '\n' + content[style_start:head_end]
    
    # Replace header
    header_start = content.find('<!-- Header -->')
    if header_start == -1:
        header_start = content.find('<header')
    header_end = content.find('</header>', header_start) + len('</header>')
    
    new_content = (
        content[:head_start] +
        new_head +
        content[head_end:header_start] +
        INDEX_HEADER + '\n' +
        content[header_end:]
    )
    
    with open('shopping-guide.html', 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print("✅ Fixed shopping-guide.html")

def fix_contact():
    """Fix contact.html"""
    with open('contact.html', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Replace head content
    head_start = content.find('<head>') + len('<head>\n')
    head_end = content.find('</head>')
    
    # Find where styles start (keep page-specific styles)
    style_start = content.find('<style>', head_start)
    
    new_head = INDEX_HEAD + '\n' + content[style_start:head_end]
    
    # Replace header
    header_start = content.find('<!-- Header -->')
    if header_start == -1:
        header_start = content.find('<header')
    header_end = content.find('</header>', header_start) + len('</header>')
    
    new_content = (
        content[:head_start] +
        new_head +
        content[head_end:header_start] +
        INDEX_HEADER + '\n' +
        content[header_end:]
    )
    
    with open('contact.html', 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print("✅ Fixed contact.html")

# Fix both files
fix_shopping_guide()
fix_contact()

print("\n✅ Both files now have identical headers to index.html!")
