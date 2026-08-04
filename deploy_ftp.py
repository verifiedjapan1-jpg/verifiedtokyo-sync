import os
import sys
import subprocess

host = os.environ.get('SSH_HOST')
user = os.environ.get('SSH_USER')
key = os.environ.get('SSH_PRIVATE_KEY')

if not host or not user or not key:
    print('❌ Missing SSH environment variables!')
    sys.exit(1)

# 秘密鍵を一時ファイルに保存
key_path = '/tmp/deploy_key'
with open(key_path, 'w') as f:
    f.write(key)
os.chmod(key_path, 0o600)

remote_path = f'/home/xs365153/verifiedtokyo.com/public_html/'

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
    if not os.path.exists(filename):
        print(f'⚠️ {filename} not found, skipping.')
        continue
    print(f'📤 Uploading {filename}...')
    cmd = [
        'scp',
        '-P', '10022',
        '-i', key_path,
        '-o', 'StrictHostKeyChecking=no',
        filename,
        f'{user}@{host}:{remote_path}{filename}'
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode == 0:
        print(f'  ✅ {filename} uploaded successfully.')
    else:
        print(f'  ❌ Failed: {result.stderr}')
        sys.exit(1)

os.remove(key_path)
print('🎉 All files deployed successfully!')
