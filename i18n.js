const TRANSLATIONS = {
    'Home': {'ja': 'ホーム'},
    'Products': {'ja': '商品一覧'},
    'Shopping Guide': {'ja': 'ショッピングガイド'},
    'Contact': {'ja': 'お問い合わせ'},
    'All Products': {'ja': 'すべての商品'},
    'In Stock Only': {'ja': '在庫ありのみ'},
    'All Brands': {'ja': 'すべてのブランド'},
    'Default': {'ja': 'デフォルト'},
    'Price: Low to High': {'ja': '価格: 安い順'},
    'Price: High to Low': {'ja': '価格: 高い順'},
    'Brand': {'ja': 'ブランド名順'},
    'All Categories': {'ja': 'すべてのカテゴリー'},
    'Bags': {'ja': 'バッグ'},
    'Wallets & Accessories': {'ja': 'お財布・小物'},
    'Watches': {'ja': 'ウォッチ'},
    'Apparel & Clothing': {'ja': 'ウェア・アパレル'},
    'Belts & Scarves': {'ja': 'ベルト・スカーフ'},
    'Search products...': {'ja': '商品を検索...'},
    'Loading products...': {'ja': '商品を読み込み中...'},
    'SOLD OUT': {'ja': '売り切れ'},
    'Sold Out': {'ja': '売り切れ'},
    'View Detail': {'ja': '詳細を見る'},
    'Description': {'ja': '商品説明'},
    'Back to Products': {'ja': '商品一覧に戻る'},
    'Buy Now — ': {'ja': '購入する — '},
    'Price': {'ja': '価格'},
    'Condition': {'ja': '状態'},
    'Featured Products': {'ja': 'おすすめ商品'},
    'View All Products': {'ja': 'すべての商品を見る'},
    'New Arrivals': {'ja': '新着アイテム'},
    'Shop Premium Bags': {'ja': 'プレミアムバッグを探す'},
    'Find your perfect authentic luxury bag today.': {'ja': 'あなたにぴったりの本物のラグジュアリーバッグを見つけましょう。'}
};

let currentLang = localStorage.getItem('vt_lang') || 'en';
let currentCurr = localStorage.getItem('vt_curr') || 'USD';
let exchangeRates = JSON.parse(localStorage.getItem('vt_rates') || 'null');

async function fetchRates() {
    if (exchangeRates && Date.now() - exchangeRates.timestamp < 1000 * 60 * 60) {
        return;
    }
    try {
        const res = await fetch('https://open.er-api.com/v6/latest/USD');
        const data = await res.json();
        exchangeRates = {
            rates: data.rates,
            timestamp: Date.now()
        };
        localStorage.setItem('vt_rates', JSON.stringify(exchangeRates));
    } catch(e) {
        console.error('Failed to fetch rates', e);
        exchangeRates = { rates: { USD: 1, JPY: 155, EUR: 0.92 }, timestamp: Date.now() };
    }
}

function t(text) {
    if (currentLang === 'en') return text;
    return (TRANSLATIONS[text] && TRANSLATIONS[text][currentLang]) || text;
}

function updateUI() {
    document.querySelectorAll('[data-i18n]').forEach(el => {
        const key = el.getAttribute('data-i18n');
        if (el.tagName === 'INPUT' && el.type === 'text') {
            el.placeholder = t(key);
        } else {
            el.textContent = t(key);
        }
    });

    document.querySelectorAll('#lang-selector').forEach(sel => sel.value = currentLang);
    document.querySelectorAll('#curr-selector').forEach(sel => sel.value = currentCurr);
}

function formatPrice(usdPrice) {
    if (!exchangeRates) return `$${usdPrice}`;
    const rate = exchangeRates.rates[currentCurr] || 1;
    let converted = usdPrice * rate;
    
    if (currentCurr === 'JPY') {
        return `¥${Math.round(converted).toLocaleString()}`;
    } else if (currentCurr === 'EUR') {
        return `€${Math.round(converted).toLocaleString()}`;
    }
    return `$${Math.round(usdPrice).toLocaleString()}`;
}

function setLang(lang) {
    currentLang = lang;
    localStorage.setItem('vt_lang', lang);
    updateUI();
    if (window.onLangCurrChange) window.onLangCurrChange();
}

function setCurr(curr) {
    currentCurr = curr;
    localStorage.setItem('vt_curr', curr);
    if (window.onLangCurrChange) window.onLangCurrChange();
}

document.addEventListener('DOMContentLoaded', async () => {
    await fetchRates();
    updateUI();

    document.querySelectorAll('#lang-selector').forEach(sel => {
        sel.addEventListener('change', e => setLang(e.target.value));
    });
    
    document.querySelectorAll('#curr-selector').forEach(sel => {
        sel.addEventListener('change', e => setCurr(e.target.value));
    });

    if (window.onLangCurrChange) window.onLangCurrChange();
});
