import os
import sys
import ftplib

host = os.environ.get('FTP_HOST') or os.environ.get('SSH_HOST') or 'sv16666.xserver.jp'
user = os.environ.get('FTP_USER') or os.environ.get('SSH_USER') or 'deploy@verifiedtokyo.com'
passwd = os.environ.get('FTP_PASSWORD') or os.environ.get('SSH_PASSWORD')

if not passwd:
    print('❌ Missing FTP_PASSWORD environment variable!')
    sys.exit(1)

print(f'🔌 Connecting to FTPS server: {host} as {user}...')

try:
    ftp = ftplib.FTP_TLS(host)
    ftp.login(user, passwd)
    ftp.prot_p()
    print(f'✅ Connected & authenticated! Current directory (pwd): {ftp.pwd()}')
    print(f'📂 Initial file list: {ftp.nlst()[:10]}')

    # Check if target subdirectories exist (e.g. verifiedtokyo.com/public_html or public_html)
    dir_list = ftp.nlst()
    target_dir = None
    if 'verifiedtokyo.com' in dir_list:
        target_dir = 'verifiedtokyo.com/public_html'
    elif 'verifdtokyo.com' in dir_list:
        target_dir = 'verifdtokyo.com/public_html'
    elif 'public_html' in dir_list:
        target_dir = 'public_html'

    if target_dir:
        print(f'📁 Changing remote directory to: {target_dir}')
        ftp.cwd(target_dir)
        print(f'📍 New current directory: {ftp.pwd()}')

    files_to_upload = [
        'products_data.json',
        'products.html',
        'index.html',
        'contact.html',
        'shopping-guide.html',
        'product-detail.html',
        'styles.css',
        'mobile-menu.js'
    ]

    for filename in files_to_upload:
        if os.path.exists(filename):
            print(f'📤 Uploading {filename} to {ftp.pwd()}...')
            with open(filename, 'rb') as f:
                ftp.storbinary(f'STOR {filename}', f)
            print(f'  ✅ {filename} uploaded successfully.')

    ftp.quit()
    print('🎉 All files deployed to Xserver successfully!')
except Exception as e:
    print(f'❌ FTP upload error: {e}')
    sys.exit(1)
