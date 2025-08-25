import requests
from django.conf import settings

def get_live_stock_price(symbol):
    """
    Fetches the live price for a given stock symbol using the Polygon.io API.
    """
    api_key = 'lDsVOlmP4xIv4adyCEE7du8aSt41_ORg'
    
    # Use the Polygon.io snapshot endpoint for the latest trade information.
    # The symbol is converted to uppercase to match API requirements.
    url = f"https://api.polygon.io/v2/snapshot/locale/us/markets/stocks/tickers/{symbol.upper()}"
    
    try:
        response = requests.get(url, params={'apiKey': api_key})
        response.raise_for_status()
        data = response.json()
        
        # Access the last price from the snapshot data.
        if 'ticker' in data and 'lastTrade' in data['ticker'] and 'p' in data['ticker']['lastTrade']:
            return data['ticker']['lastTrade']['p']
        else:
            print(f"No last trade data available for {symbol}.")
            return None
        
    except requests.exceptions.RequestException as e:
        print(f"Error fetching Polygon.io price for {symbol}: {e}")
        return None