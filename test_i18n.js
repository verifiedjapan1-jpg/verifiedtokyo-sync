const currentCurr = 'JPY';
const exchangeRates = null;

function formatPrice(productOrPrice) {
    let p = productOrPrice;
    
    // Fallback if just a number is passed (for safety)
    if (typeof p === 'number' || typeof p === 'string') {
        let val = parseFloat(p);
        if (currentCurr === 'JPY') {
            const rate = exchangeRates ? (exchangeRates.rates['JPY'] || 155) : 155;
            let converted = Math.round((val * rate) / 100) * 100;
            return `¥${converted.toLocaleString()}`;
        } else if (currentCurr === 'EUR') {
            const rate = exchangeRates ? (exchangeRates.rates['EUR'] || 0.92) : 0.92;
            let converted = Math.round((val * rate) / 100) * 100;
            return `€${converted.toLocaleString()}`;
        }
        let converted = Math.round(val / 100) * 100;
        return `$${converted.toLocaleString()}`;
    }

    // Main logic when full product object is passed
    if (currentCurr === 'JPY') {
        let val = p.price_jpy_final;
        if (!val) {
            // Fallback for old data: convert USD price to JPY
            const rate = exchangeRates ? (exchangeRates.rates['JPY'] || 155) : 155;
            val = p.price * rate;
        }
        val = Math.round(val / 100) * 100; // Round to nearest 100
        return `¥${val.toLocaleString()}`;
    } else if (currentCurr === 'EUR') {
        let baseUsd = p.base_usd || (p.price - 300); // approximate if not present
        const rate = exchangeRates ? (exchangeRates.rates['EUR'] || 0.92) : 0.92;
        let eurBase = baseUsd * rate;
        let val = Math.round((eurBase + 300) / 100) * 100; // Round to nearest 100
        return `€${val.toLocaleString()}`;
    }
    
    // USD
    let val = p.price_usd_final || p.price;
    val = Math.round(val / 100) * 100; // Round to nearest 100
    return `$${val.toLocaleString()}`;
}

const product = {
  "id": 636,
  "name": "HERMES Clemence Birkin Handbag Red Silver Hardware HE371",
  "brand": "HERMES",
  "price": 12900.0,
  "price_usd_final": 12900.0,
  "price_jpy_final": 1980000.0,
  "base_usd": 12616.0,
};

console.log(formatPrice(product));
