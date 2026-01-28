#!/usr/bin/env python3
"""Add Entrupy authentication certificate notice to product detail page"""

import re

with open('product-detail.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Find the product detail template in JavaScript
# Look for where we create the product detail HTML

# Add authentication badge CSS
auth_badge_style = """
        .authentication-badge {
            background: linear-gradient(135deg, #1a1a1a 0%, #2c2c2c 100%);
            color: white;
            padding: 15px 20px;
            border-radius: 8px;
            margin: 20px 0;
            display: flex;
            align-items: center;
            gap: 12px;
            border-left: 4px solid #c9a86a;
        }
        
        .authentication-badge svg {
            width: 24px;
            height: 24px;
            flex-shrink: 0;
        }
        
        .authentication-badge-text {
            flex: 1;
        }
        
        .authentication-badge-text strong {
            display: block;
            font-size: 16px;
            margin-bottom: 4px;
        }
        
        .authentication-badge-text span {
            font-size: 13px;
            opacity: 0.9;
        }
"""

# Insert before </style> closing tag
content = content.replace('    </style>', auth_badge_style + '\n    </style>')

# Find where product HTML is generated and add authentication badge
# Look for the JavaScript section that creates product detail HTML
pattern = r'(innerHTML = `[\s\S]*?<div class="product-detail-description">)'

def add_auth_badge(match):
    original = match.group(1)
    # Add authentication badge right after description div opens
    auth_badge_html = '''
                <div class="authentication-badge">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <path d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"/>
                    </svg>
                    <div class="authentication-badge-text">
                        <strong>✓ Entrupy鑑定書付き</strong>
                        <span>すべての商品にEntrupy社の真贋鑑定書が付属します</span>
                    </div>
                </div>
'''
    return original + auth_badge_html

content = re.sub(pattern, add_auth_badge, content, flags=re.MULTILINE)

with open('product-detail.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ Entrupy鑑定書の情報を追加しました！")
