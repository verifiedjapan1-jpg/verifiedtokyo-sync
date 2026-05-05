const https = require('https');
const fs = require('fs');
const path = require('path');

// HTTPリクエスト
function fetchJSON(url) {
  return new Promise((resolve, reject) => {
    https.get(url, (res) => {
      let data = '';
      res.on('data', chunk => data += chunk);
      res.on('end', () => {
        try {
          resolve(JSON.parse(data));
        } catch (e) {
          reject(new Error(`JSON parse error: ${e.message}`));
        }
      });
    }).on('error', reject);
  });
}

// ページネーション対応で全商品を取得
async function fetchAllProducts() {
  let allProducts = [];
  let page = 1;
  const limit = 250;

  while (true) {
    const url = `https://t-secondhands.jp/collections/all/products.json?limit=${limit}&page=${page}&sort_by=price-descending`;
    console.log(`Fetching page ${page}... (URL: ${url})`);

    try {
      const data = await fetchJSON(url);
      const products = data.products || [];

      console.log(`Page ${page}: ${products.length} products`);

      if (products.length === 0) {
        console.log('No more products, stopping.');
        break;
      }

      allProducts = allProducts.concat(products);

      if (products.length < limit) {
        console.log('Last page reached.');
        break;
      }

      page++;

      // レート制限対策（1秒待機）
      await new Promise(resolve => setTimeout(resolve, 1000));

    } catch (error) {
      console.error(`Error on page ${page}:`, error.message);
      break;
    }
  }

  return allProducts;
}

// 商品データを変換
function transformProduct(p, index) {
  const images = p.images ? p.images.map(img => img.src) : [];
  const imageUrl = images[0] || '';
  const brand = p.title ? p.title.split(' ')[0].toUpperCase() : '';

  const bodyText = (p.body_html || '')
    .replace(/<[^>]*>/g, ' ')
    .replace(/\s+/g, ' ')
    .trim();

  const heightMatch = bodyText.match(/(?:height|H\b)[:\s]*(\d+)\s*cm/i) || bodyText.match(/(\d+)\s*cm[^]*?(?:height|H\b)/i);
  const widthMatch = bodyText.match(/(?:width|W\b)[:\s]*(\d+)\s*cm/i) || bodyText.match(/(\d+)\s*cm[^]*?(?:width|W\b)/i);
  const depthMatch = bodyText.match(/(?:depth|D\b)[:\s]*(\d+)\s*cm/i) || bodyText.match(/(\d+)\s*cm[^]*?(?:depth|D\b)/i);

  const colorMatch = bodyText.match(/Color:\s*([^\n,.<]+)/i);
  const materialMatch = bodyText.match(/Material:\s*([^\n,.<]+)/i);
  const designMatch = bodyText.match(/Design:\s*([^\n,.<]+)/i);
  const hardwareMatch = bodyText.match(/(?:Accents|Hardware):\s*([^\n,.<]+)/i);

  return {
    id: index + 1,
    name: p.title || '',
    brand: brand,
    price: Math.round(parseFloat(p.variants?.[0]?.price) || 0),
    url: `https://t-secondhands.jp/products/${p.handle}`,
    imageUrl: imageUrl,
    productId: p.handle || '',
    description: bodyText.substring(0, 200),
    dimensions: {
      height: heightMatch ? `${heightMatch[1]}cm` : '',
      width: widthMatch ? `${widthMatch[1]}cm` : '',
      depth: depthMatch ? `${depthMatch[1]}cm` : ''
    },
    specifications: {
      color: colorMatch ? colorMatch[1].trim() : '',
      material: materialMatch ? materialMatch[1].trim() : '',
      design: designMatch ? designMatch[1].trim() : '',
      hardware: hardwareMatch ? hardwareMatch[1].trim() : ''
    },
    images: images,
    detailText: {
      intro: 'We update our inventory daily, There may be sold items listed. Thank you for your understanding.',
      dimensions: {
        height: heightMatch ? `${heightMatch[1]}cm` : '',
        width: widthMatch ? `${widthMatch[1]}cm` : '',
        depth: depthMatch ? `${depthMatch[1]}cm` : ''
      },
      description: bodyText.substring(0, 300),
      specifications: [
        colorMatch ? `Color: ${colorMatch[1].trim()}` : '',
        materialMatch ? `Material: ${materialMatch[1].trim()}` : '',
        designMatch ? `Design: ${designMatch[1].trim()}` : '',
        hardwareMatch ? `Accents: ${hardwareMatch[1].trim()}` : ''
      ].filter(Boolean),
      additional: 'Stains/Tears...None'
    }
  };
}

async function main() {
  try {
    console.log('=== Starting product sync from t-secondhands.jp ===');

    const shopifyProducts = await fetchAllProducts();
    console.log(`\nTotal products fetched: ${shopifyProducts.length}`);

    if (shopifyProducts.length === 0) {
      console.error('No products fetched. Exiting.');
      process.exit(1);
    }

    const seenIds = new Set();
    const uniqueProducts = [];

    shopifyProducts.forEach((p) => {
      if (!seenIds.has(p.handle)) {
        seenIds.add(p.handle);
        uniqueProducts.push(transformProduct(p, uniqueProducts.length));
      }
    });

    console.log(`Unique products: ${uniqueProducts.length}`);

    const outputPath = path.join(__dirname, 'products.json');
    fs.writeFileSync(outputPath, JSON.stringify(uniqueProducts, null, 2), 'utf-8');

    console.log(`\n✅ Successfully saved ${uniqueProducts.length} products to products.json`);
    process.exit(0);
  } catch (error) {
    console.error('Fatal error:', error.message);
    process.exit(1);
  }
}

main();
