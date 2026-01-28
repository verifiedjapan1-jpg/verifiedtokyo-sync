#!/usr/bin/env python3
"""Swap Featured Collection and Brands sections in index.html"""

with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Find section boundaries
hero_end = content.find('    </section>', content.find('<!-- Hero Section -->')) + len('    </section>\n')

# Find first section (currently has brands content with "Featured Products Section" comment)
brands_section_start = content.find('    <!-- Featured Products Section -->', hero_end)
brands_section_end = content.find('    </script>\n    </section>', brands_section_start) + len('    </script>\n    </section>\n')
brands_section = content[brands_section_start:brands_section_end]

# Find second section (currently has products content with "Brand Section" comment)  
products_section_start = content.find('    <!-- Brand Section -->', brands_section_end)
products_section_end = content.find('    </section>', products_section_start) + len('    </section>\n')
products_section = content[products_section_start:products_section_end]

# Find footer
footer_start = content.find('    <!-- Footer -->')

# Reconstruct with swapped sections
new_content = (
    content[:hero_end] + '\n' +
    products_section.replace('<!-- Brand Section -->', '<!-- Featured Products Section -->').replace('brands-section', 'products-section') + '\n' +
    brands_section.replace('<!-- Featured Products Section -->', '<!-- Brands Section -->').replace('products-section', 'brands-section') + '\n' +
    content[footer_start:]
)

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(new_content)

print("✅ Sections swapped successfully!")
print(f"- Brands section was at: {brands_section_start}-{brands_section_end}")
print(f"- Products section was at: {products_section_start}-{products_section_end}")
