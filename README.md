# Vinci-Vantage

NFT Market Scanner & Trading Bot Protocol

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Configure your API key in `.env`:
```
MARKET_API_KEY=your_api_key_here
```

3. Run the bot:
```bash
python vinci_bot.py
```

## Configuration

Edit `vinci_bot.py` to configure:
- `TARGET_COLLECTION` - The NFT collection to monitor
- `MAX_PRICE_ETH` - Maximum price threshold
- `CHECK_INTERVAL` - How often to scan (seconds)

## ⚠️ Security

Never commit your `.env` file with API keys!
