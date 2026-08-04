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
    print(f'✅ Connected & authenticated! Web root directory (pwd): {ftp.pwd()}')

    # Upload files directly to root directory (sub-FTP home directory is already public_html)
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
            print(f'📤 Uploading {filename} ({os.path.getsize(filename)} bytes) to web root...')
            with open(filename, 'rb') as f:
                res = ftp.storbinary(f'STOR {filename}', f)
                print(f'  ✅ Response for {filename}: {res}')

    ftp.quit()
    print('🎉 All files deployed to Xserver web root successfully!')
except Exception as e:
    print(f'❌ FTP upload error: {e}')
    sys.exit(1)
