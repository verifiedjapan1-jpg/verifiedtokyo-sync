import glob, os

files = glob.glob('*.html')

header_addon = """
                <div class="lang-curr-container" style="display:flex; gap:10px; margin-left:15px;">
                    <select id="curr-selector" style="border:none; background:transparent; font-size:12px; cursor:pointer; outline:none; font-weight:600;">
                        <option value="USD">USD $</option>
                        <option value="JPY">JPY ¥</option>
                        <option value="EUR">EUR €</option>
                    </select>
                    <select id="lang-selector" style="border:none; background:transparent; font-size:12px; cursor:pointer; outline:none; font-weight:600;">
                        <option value="en">EN</option>
                        <option value="ja">JP</option>
                    </select>
                </div>
"""

def add_i18n(html):
    # Add i18n script before closing body
    if '<script src="i18n.js"></script>' not in html:
        html = html.replace('</body>', '    <script src="i18n.js"></script>\n</body>')
    
    # Insert dropdowns into header (right after search icon or search container)
    search_closing = '</div>\n                                </div>'
    if 'lang-curr-container' not in html:
        if '<div class="mobile-menu-toggle"' in html:
            # We want to insert the container before mobile-menu-toggle
            parts = html.split('<div class="mobile-menu-toggle"')
            html = parts[0] + header_addon + '                <div class="mobile-menu-toggle"' + parts[1]
    
    # Add data-i18n attributes for static nav
    html = html.replace('>Home<', ' data-i18n="Home">Home<')
    html = html.replace('>Products<', ' data-i18n="Products">Products<')
    html = html.replace('>Shopping Guide<', ' data-i18n="Shopping Guide">Shopping Guide<')
    html = html.replace('>Contact<', ' data-i18n="Contact">Contact<')
    html = html.replace('placeholder="Search products..."', 'placeholder="Search products..." data-i18n="Search products..."')
    
    return html

for f in files:
    with open(f, 'r') as file:
        content = file.read()
    content = add_i18n(content)
    with open(f, 'w') as file:
        file.write(content)
print("Updated all HTML files!")
