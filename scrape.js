const https = require('https');
const fs = require('fs');
const path = require('path');

async function fetchFromShopifyAPI(url) {
  return new Promise((resolve, reject) => {
    https.get(url, (res) => {
      let data = '';
      res.on('data', chunk => data += chunk);
      res.on('end', () => {
        try {
          resolve(JSON.parse(data));
        } catch (e) {
          reject(e);
        }
      });
    }).on('error', reject);
  });
}

async function scrapeProducts() {
  try {
    console.log('Fetching all products from t-secondhands.jp...');
    
    // Shopify API - 全商品を取得（制限なし）
    const apiUrl = 'https://t-secondhands.jp/collections/all/products.json?limit=250&sort_by=price-descending';
    
    const data = await fetchFromShopifyAPI(apiUrl);
    const shopifyProducts = data.products || [];
    
    console.log(`Found ${shopifyProducts.length} total products`);
    
    // 既存データを読み込み
    const existingProducts = loadExistingData();
    const nextId = (existingProducts[existingProducts.length - 1]?.id || 0) + 1;
    
    // **全ての商品を処理（制限なし）**
    const newProducts = shopifyProducts.map((p, idx) => transformProduct(p, nextId + idx));
    
    console.log(`Transformed ${newProducts.length} new products`);
    
    // 重複排除
    const allProducts = [...existingProducts, ...newProducts];
    const uniqueProducts = [];
    const seenIds = new Set();
    
    for (const product of allProducts) {
      if (!seenIds.has(product.productId)) {
        uniqueProducts.push(product);
        seenIds.add(product.productId);
      }
    }
    
    // ファイルに保存
    const outputPath = path.join(__dirname, 'products.json');
    fs.writeFileSync(outputPath, JSON.stringify(uniqueProducts, null, 2), 'utf-8');
    
    console.log(`✅ Saved ${uniqueProducts.length} products to products.json`);
    process.exit(0);
    
  } catch (error) {
    console.error('❌ Error:', error.message);
    process.exit(1);
  }
}

function transformProduct(p, index) {
  const images = p.images ? p.images.map(img => img.src) : [];
  const imageUrl = images[0] || '';
  const brand = p.title ? p.title.split(' ')[0].toUpperCase() : '';
  
  return {
    id: index,
    name: p.title || '',
    brand: brand,
    price: Math.round(p.variants?.[0]?.price || 0),
    url: `https://t-secondhands.jp/products/${p.handle}`,
    imageUrl: imageUrl,
    productId: p.handle || '',
    description: (p.body_html || '').substring(0, 100),
    dimensions: { height: '', width: '', depth: '' },
    specifications: { color: '', material: '', design: '', hardware: '' },
    images: images,
    detailText: {
      intro: 'We update our inventory daily',
      dimensions: { height: '', width: '', depth: '' },
      description: p.title || '',
      specifications: [],
      additional: 'Condition: Used'
    }
  };
}

function loadExistingData() {
  const dataFile = path.join(__dirname, 'products.json');
  if (fs.existsSync(dataFile)) {
    try {
      return JSON.parse(fs.readFileSync(dataFile, 'utf-8'));
    } catch (e) {
      return [];
    }
  }
  return [];
}

scrapeProducts();
