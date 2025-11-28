"""
Cryptocurrency Watchlist

This module contains the list of cryptocurrencies to monitor.
Symbols are in Yahoo Finance format (e.g., BTC-USD, ETH-USD).
"""

# Major Cryptocurrencies
MAJOR_CRYPTOS = [
    'BTC-USD',      # Bitcoin
    'ETH-USD',      # Ethereum
    'BNB-USD',      # Binance Coin
    'XRP-USD',      # Ripple
    'ADA-USD',      # Cardano
    'DOGE-USD',     # Dogecoin
    'SOL-USD',      # Solana
    'DOT-USD',      # Polkadot
    'POL28321-USD',    # Polygon
    'LTC-USD',      # Litecoin
]

# DeFi & Layer 2
DEFI_CRYPTOS = [
    'UNI7083-USD',      # Uniswap
    'LINK-USD',     # Chainlink
    'AVAX-USD',     # Avalanche
    'ATOM-USD',     # Cosmos
    'AAVE-USD',     # Aave
    'CRV-USD',      # Curve
    'MKR-USD',      # Maker
]

# Alternative Coins
ALT_CRYPTOS = [
    'SHIB-USD',     # Shiba Inu
    'APT21794-USD',      # Aptos
    'ARB-USD',      # Arbitrum
    'OP-USD',       # Optimism
    'INJ-USD',      # Injective
    'SUI20947-USD',      # Sui
    'SEI-USD',      # Sei
    'TIA-USD',      # Celestia
]

# Stablecoins (for reference, usually not alerted)
STABLECOINS = [
    'USDT-USD',     # Tether
    'USDC-USD',     # USD Coin
    'DAI-USD',      # Dai
]

# =============================================================================
# DEFAULT WATCHLIST
# =============================================================================

# Combine lists for default watchlist
CRYPTO_WATCHLIST = MAJOR_CRYPTOS + DEFI_CRYPTOS + ALT_CRYPTOS

# =============================================================================
# CATEGORY MAPPING
# =============================================================================

CATEGORY_MAP = {
    # Major
    'BTC-USD': 'Major',
    'ETH-USD': 'Major',
    'BNB-USD': 'Major',
    'XRP-USD': 'Major',
    'ADA-USD': 'Major',
    'DOGE-USD': 'Major',
    'SOL-USD': 'Major',
    'DOT-USD': 'Major',
    'MATIC-USD': 'Major',
    'LTC-USD': 'Major',

    # DeFi
    'UNI-USD': 'DeFi',
    'LINK-USD': 'DeFi',
    'AVAX-USD': 'DeFi',
    'ATOM-USD': 'DeFi',
    'AAVE-USD': 'DeFi',
    'CRV-USD': 'DeFi',
    'MKR-USD': 'DeFi',

    # Alt
    'SHIB-USD': 'Alt',
    'APT-USD': 'Alt',
    'ARB-USD': 'Alt',
    'OP-USD': 'Alt',
    'INJ-USD': 'Alt',
    'SUI-USD': 'Alt',
    'SEI-USD': 'Alt',
    'TIA-USD': 'Alt',
}


def get_crypto_category(symbol: str) -> str:
    """Get the category for a crypto symbol."""
    return CATEGORY_MAP.get(symbol, 'Unknown')


def get_crypto_name(symbol: str) -> str:
    """Get human-readable name from symbol."""
    names = {
        'BTC-USD': 'Bitcoin',
        'ETH-USD': 'Ethereum',
        'BNB-USD': 'Binance Coin',
        'XRP-USD': 'Ripple',
        'ADA-USD': 'Cardano',
        'DOGE-USD': 'Dogecoin',
        'SOL-USD': 'Solana',
        'DOT-USD': 'Polkadot',
        'MATIC-USD': 'Polygon',
        'LTC-USD': 'Litecoin',
        'UNI-USD': 'Uniswap',
        'LINK-USD': 'Chainlink',
        'AVAX-USD': 'Avalanche',
        'ATOM-USD': 'Cosmos',
        'AAVE-USD': 'Aave',
        'CRV-USD': 'Curve',
        'MKR-USD': 'Maker',
        'SHIB-USD': 'Shiba Inu',
        'APT-USD': 'Aptos',
        'ARB-USD': 'Arbitrum',
        'OP-USD': 'Optimism',
        'INJ-USD': 'Injective',
        'SUI-USD': 'Sui',
        'SEI-USD': 'Sei',
        'TIA-USD': 'Celestia',
    }
    return names.get(symbol, symbol.replace('-USD', ''))
