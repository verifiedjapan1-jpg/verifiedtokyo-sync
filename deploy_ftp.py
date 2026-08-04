import os
import sys
import ftplib

host = os.environ.get('FTP_HOST')
user = os.environ.get('FTP_USER')
passwd = os.environ.get('FTP_PASSWORD')

if not host or not user or not passwd:
    print('❌ Missing FTP environment variables!')
    sys.exit(1)

print(f'🔌 Connecting to FTPS server: {host} as {user}...')

try:
    ftp = ftplib.FTP_TLS(host)
    ftp.login(user, passwd)
    ftp.prot_p()
    ftp.set_pasv(True)
    print('✅ Connected & authenticated successfully!')

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
            filesize = os.path.getsize(filename)
            print(f'📤 Uploading {filename} ({filesize} bytes)...')
            with open(filename, 'rb') as f:
                ftp.storbinary(f'STOR {filename}', f, blocksize=65536)
            print(f'  ✅ {filename} uploaded successfully.')
        else:
            print(f'  ⚠️ {filename} not found, skipping.')

    ftp.quit()
    print('🎉 All files deployed to Xserver successfully!')

except Exception as e:
    print(f'❌ FTP upload error: {e}')
    import traceback
    traceback.print_exc()
    sys.exit(1)
