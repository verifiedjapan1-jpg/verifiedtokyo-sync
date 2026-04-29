const https = require('https');
const fs = require('fs');
const path = require('path');

// t-secondhands.jp から商品データを取得
async function fetchProducts() {
  const url = 'https://t-secondhands.jp/ja/collections/all.json?sort_by=price-descending&limit=250';
  
  return new Promise((resolve, reject) => {
    https.get(url, (res) => {
      let data = '';
      res.on('data', chunk => data += chunk);
      res.on('end', () => {
        try {
          const json = JSON.parse(data);
          resolve(json.products || []);
        } catch (e) {
          reject(e);
        }
      });
    }).on('error', reject);
  });
}

// 各商品の詳細情報を取得
async function fetchProductDetail(productUrl) {
  return new Promise((resolve, reject) => {
    https.get(productUrl + '.json', (res) => {
      let data = '';
      res.on('data', chunk => data += chunk);
      res.on('end', () => {
        try {
          const json = JSON.parse(data);
          resolve(json.product || {});
        } catch (e) {
          // エラー時は空オブジェクトを返す
          resolve({});
        }
      });
    }).on('error', reject);
  });
}

// Shopify の商品データを統一形式に変換
function transformProduct(shopifyProduct, index) {
  const images = shopifyProduct.images ? shopifyProduct.images.map(img => img.src) : [];
  const imageUrl = images[0] || '';
  
  // ブランド名は title から抽出（最初の単語）
  const brand = shopifyProduct.title ? shopifyProduct.title.split(' ')[0].toUpperCase() : '';
  
  // 仕様情報を抽出
  const specifications = {
    color: '',
    material: '',
    design: '',
    hardware: ''
  };
  
  if (shopifyProduct.body_html) {
    const text = shopifyProduct.body_html;
    // 簡易的に抽出（実際はもっと複雑になる可能性）
    if (text.includes('Leather')) specifications.material = 'Leather';
    if (text.includes('Canvas')) specifications.material = 'Canvas';
  }
  
  // 寸法情報
  const dimensions = {
    height: '',
    width: '',
    depth: ''
  };
  
  return {
    id: index + 1,
    name: shopifyProduct.title || '',
    brand: brand,
    price: Math.round(shopifyProduct.variants?.[0]?.price || 0),
    url: `https://t-secondhands.jp/ja/products/${shopifyProduct.handle}`,
    imageUrl: imageUrl,
    productId: shopifyProduct.handle || '',
    description: (shopifyProduct.body_html || '').substring(0, 100) + '...',
    dimensions: dimensions,
    specifications: specifications,
    images: images,
    detailText: {
      intro: 'We update our inventory daily, There may be sold items listed. Thank you for your understanding.',
      dimensions: { height: '', width: '', depth: '' },
      description: shopifyProduct.title || '',
      specifications: [],
      additional: 'Condition: Used'
    }
  };
}

// 既存データを読み込む
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

// 重複をチェック（productId で比較）
function filterNewProducts(newProducts, existingProducts) {
  const existingIds = new Set(existingProducts.map(p => p.productId));
  return newProducts.filter(p => !existingIds.has(p.productId));
}

// メイン処理
async function main() {
  try {
    console.log('Starting scrape...');
    
    // 既存データを読み込む
    const existingProducts = loadExistingData();
    const nextId = (existingProducts[existingProducts.length - 1]?.id || 0) + 1;
    
    // t-secondhands.jp から商品リストを取得
    console.log('Fetching product list from t-secondhands.jp...');
    const shopifyProducts = await fetchProducts();
    
    // 新規商品のみフィルタリング
    console.log(`Found ${shopifyProducts.length} total products`);
    
    // 各商品を変換
    const newProducts = shopifyProducts
      .map((p, idx) => transformProduct(p, nextId + idx))
      .slice(0, 100); // 最初の100件のみ（APIリミット対策）
    
    console.log(`Transformed ${newProducts.length} new products`);
    
    // 既存データと結合
    const allProducts = [...existingProducts, ...newProducts];
    
    // 重複排除（productId で）
    const uniqueProducts = [];
    const seenIds = new Set();
    for (const p of allProducts) {
      if (!seenIds.has(p.productId)) {
        uniqueProducts.push(p);
        seenIds.add(p.productId);
      }
    }
    
    // JSON ファイルに保存
    const outputPath = path.join(__dirname, 'products.json');
    fs.writeFileSync(outputPath, JSON.stringify(uniqueProducts, null, 2), 'utf-8');
    
    console.log(`✅ Saved ${uniqueProducts.length} products to products.json`);
    console.log('Scrape completed successfully!');
    
    process.exit(0);
  } catch (error) {
    console.error('❌ Error:', error.message);
    process.exit(1);
  }
}

main();
