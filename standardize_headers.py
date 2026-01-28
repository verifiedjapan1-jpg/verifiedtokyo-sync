#!/usr/bin/env python3
"""Standardize headers across all pages to match index.html"""

# Standard header HTML from index.html
STANDARD_HEADER = '''    <!-- Header -->
    <header class="header">
        <div class="main-header">
            <div class="container">
                <div class="logo-nav-container">
                    <div>
                        <a href="index.html" style="text-decoration: none; color: inherit;">
                            <h1 class="logo">Verified Tokyo</h1>
                        </a>
                        <p class="tagline">Premium Pre-Owned Luxury</p>
                    </div>
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

def update_header(filename):
    """Update header in given file"""
    with open(filename, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find header start and end
    header_start = content.find('<!--Header')
    if header_start == -1:
        header_start = content.find('<header')
    
    if header_start == -1:
        print(f"❌ Could not find header in {filename}")
        return False
    
    # Find header end
    header_end = content.find('</header>', header_start) + len('</header>')
    
    if header_end <= len('</header>'):
        print(f"❌ Could not find header end in {filename}")
        return False
    
    # Replace header
    new_content = content[:header_start] + STANDARD_HEADER + content[header_end:]
    
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print(f"✅ Updated header in {filename}")
    return True

# Update all pages except index.html
files = ['shopping-guide.html', 'contact.html']

for file in files:
    update_header(file)

print("\\n✅ All headers standardized!")
