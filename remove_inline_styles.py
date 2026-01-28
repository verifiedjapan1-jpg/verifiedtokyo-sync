#!/usr/bin/env python3
"""Remove inline header styles from shopping-guide.html and contact.html"""

import re

def remove_header_styles(filename):
    """Remove any inline styles that affect header"""
    with open(filename, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find and remove <style> tags that contain header/nav styles
    # We'll look for style tags and remove header-related CSS
    style_pattern = r'<style>.*?</style>'
    
    def filter_styles(match):
        style_content = match.group(0)
        # Keep only non-header styles
        if any(keyword in style_content for keyword in ['.header', '.logo', '.main-header', 'nav', '.main-nav']):
            # Remove header-related styles but keep other styles
            lines = style_content.split('\n')
            filtered_lines = []
            skip = False
            for line in lines:
                if any(keyword in line for keyword in ['.header', '.logo', '.main-header', '.logo-nav-container', 'nav ']):
                    skip = True
                if skip and '}' in line:
                    skip = False
                    continue
                if not skip and line.strip():
                    filtered_lines.append(line)
            return '\n'.join(filtered_lines) if filtered_lines else ''
        return style_content
    
    # Process the content
    new_content = re.sub(style_pattern, filter_styles, content, flags=re.DOTALL)
    
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print(f"✅ Removed header styles from {filename}")

# Process both files
for file in ['shopping-guide.html', 'contact.html']:
    remove_header_styles(file)

print("\n✅ Header styles removed from both files!")
print("Now all pages will use styles.css for consistent header design")
