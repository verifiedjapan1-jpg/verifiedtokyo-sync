import glob, re

files = glob.glob('*.html')
if 'test-dimensions.html' in files:
    files.remove('test-dimensions.html')

lang_block = """<div class="lang-curr-container" style="display:flex; gap:10px; margin-left:15px;">
                    <select id="curr-selector" style="border:none; background:transparent; font-size:12px; cursor:pointer; outline:none; font-weight:600;">
                        <option value="USD">USD $</option>
                        <option value="JPY">JPY ¥</option>
                        <option value="EUR">EUR €</option>
                    </select>
                    <select id="lang-selector" style="border:none; background:transparent; font-size:12px; cursor:pointer; outline:none; font-weight:600;">
                        <option value="en">EN</option>
                        <option value="ja">JP</option>
                    </select>
                </div>"""

for f in files:
    with open(f, 'r') as file:
        content = file.read()
    
    # Remove existing lang-curr-container blocks (however many lines they are)
    # The block has <div class="lang-curr-container"...> ... </div>
    # Using regex to remove it
    content = re.sub(r'<div class="lang-curr-container".*?</div>', '', content, flags=re.DOTALL)
    
    # Find the search icon closing div and insert it there
    # The search icon is <div class="search-icon" onclick="performSearch()"> ... </div>
    # We want to insert right after the closing </div> of search-icon
    
    search_icon_pattern = r'(<div class="search-icon" onclick="performSearch\(\)">\s*<svg.*?</svg>\s*</div>)'
    
    # Replace search_icon block with search_icon + lang_block
    if re.search(search_icon_pattern, content, flags=re.DOTALL):
        content = re.sub(search_icon_pattern, r'\1\n                ' + lang_block, content, flags=re.DOTALL)
    
    with open(f, 'w') as file:
        file.write(content)
        
print("Layout fixed!")
