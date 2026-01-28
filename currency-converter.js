// Simple USD Price Formatter
// Prices in JSON are stored directly in USD (already includes $200 markup)

// Format USD price
function formatUSD(usdPrice) {
    // Round to nearest dollar and format with commas
    const rounded = Math.round(usdPrice);
    return `$${rounded.toLocaleString()}`;
}

// No initialization needed - prices are already in USD
console.log('USD price formatter loaded');
