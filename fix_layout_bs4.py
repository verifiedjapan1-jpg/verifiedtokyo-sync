import glob
from bs4 import BeautifulSoup

for f in glob.glob('*.html'):
    if f == 'test-dimensions.html': continue
    
    with open(f, 'r') as file:
        soup = BeautifulSoup(file, 'html.parser')
    
    # Find lang-curr-container
    lang_curr = soup.find('div', class_='lang-curr-container')
    search_container = soup.find('div', class_='search-container')
    
    if lang_curr and search_container:
        # Move it after search-container
        lang_curr.extract()
        search_container.insert_after(lang_curr)
        
        with open(f, 'w') as file:
            file.write(str(soup))
            
print("Layout fixed with BS4!")
