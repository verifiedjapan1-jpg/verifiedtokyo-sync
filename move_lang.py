import glob

files = glob.glob('*.html')
for f in files:
    with open(f, 'r') as file:
        content = file.read()
    
    # We want to find the exact block and move it.
    # The block is:
    #                 <div class="lang-curr-container" style="display:flex; gap:10px; margin-left:15px;">
    # ...
    #                 </div>
    # It is right before:
    #                 <div class="mobile-menu-toggle" id="mobile-menu-toggle">

    lang_start = '                <div class="lang-curr-container"'
    if lang_start in content:
        start_idx = content.find(lang_start)
        
        # Find the end of this div block
        end_str = '                <div class="mobile-menu-toggle" id="mobile-menu-toggle">'
        end_idx = content.find(end_str)
        
        if start_idx != -1 and end_idx != -1:
            # Extract the lang block (including trailing spaces before mobile-menu)
            lang_block = content[start_idx:end_idx]
            
            # Remove from original
            content = content[:start_idx] + content[end_idx:]
            
            # Now find where to insert it: inside search-container.
            # search-container ends with:
            #                     </div>
            #                 </div>
            # We want to insert it right before the last </div> of search-container.
            # So we look for the search-icon block
            search_icon_end = '                    </div>\n                </div>'
            if search_icon_end in content:
                # Replace it with the end + the lang block inside it
                replacement = '                    </div>\n' + lang_block.rstrip() + '\n                </div>'
                content = content.replace(search_icon_end, replacement)
            
            with open(f, 'w') as out_file:
                out_file.write(content)
print("Moved lang-curr-container inside search-container in all files!")
