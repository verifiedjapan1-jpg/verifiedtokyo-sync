const fs = require('fs');
const path = require('path');
const Client = require('ftp');

async function uploadToFTP() {
  return new Promise((resolve, reject) => {
    const c = new Client();
    
    const config = {
      host: process.env.FTP_HOST || 'sv16666.xserver.jp',
      user: process.env.FTP_USER || 'deploy@verifiedtokyo.com',
      password: process.env.FTP_PASSWORD,
    };
    
    if (!config.password) {
      reject(new Error('FTP_PASSWORD environment variable is not set'));
      return;
    }
    
    c.on('error', reject);
    c.on('close', () => console.log('✅ FTP connection closed'));
    
    c.on('ready', () => {
      console.log('📡 Connected to FTP server');
      
      const localFile = path.join(__dirname, 'products.json');
      const remoteFile = '/public_html/data/products.json';
      
      // リモートディレクトリが存在するか確認、なければ作成
      c.list('/public_html/data', (err, list) => {
        if (err) {
          // ディレクトリが存在しないので作成
          c.mkdir('/public_html/data', (err) => {
            if (err && err.code !== 550) { // 550: directory already exists
              reject(err);
              return;
            }
            uploadFile();
          });
        } else {
          uploadFile();
        }
      });
      
      function uploadFile() {
        const rs = fs.createReadStream(localFile);
        c.put(rs, remoteFile, (err) => {
          if (err) {
            reject(err);
          } else {
            console.log(`✅ Uploaded products.json to ${remoteFile}`);
            c.end();
            resolve();
          }
        });
      }
    });
    
    c.connect(config);
  });
}

async function main() {
  try {
    console.log('Starting FTP upload...');
    await uploadToFTP();
    console.log('FTP upload completed!');
    process.exit(0);
  } catch (error) {
    console.error('❌ FTP Error:', error.message);
    process.exit(1);
  }
}

main();
