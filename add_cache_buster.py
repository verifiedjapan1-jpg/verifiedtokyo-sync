#!/usr/bin/env python3
"""Force CSS update with timestamp to bypass cache"""

import time

with open('product-detail.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Add timestamp comment to force cache refresh
timestamp = str(int(time.time()))
cache_buster = f'\n        /* Cache buster: {timestamp} */\n'

# Find the style section and add cache buster
if '/* Cache buster:' not in content:
    content = content.replace('    </style>', cache_buster + '    </style>')
    
    with open('product-detail.html', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"✅ キャッシュバスターを追加しました: {timestamp}")
    print("ブラウザでスーパーリロード（Cmd+Shift+R）を実行してください")
else:
    print("既にキャッシュバスターが存在します")
