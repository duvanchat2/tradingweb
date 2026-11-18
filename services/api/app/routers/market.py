from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException
from app.routers.auth import CURRENCIES
from app.services.marketdata import MarketDataProvider, get_market_provider, Ticker

router = APIRouter(prefix='/api/market', tags=['market'])
Provider = Annotated[MarketDataProvider, Depends(get_market_provider)]

@router.get('/prices')
def prices(provider: Provider):
    return {'demo_mode':True, 'quote_currency':'USDT',
            'prices':{symbol:str(provider.get_price(symbol)) for symbol in CURRENCIES}}

@router.get('/landing')
def landing_prices(provider: Provider):
    """Compact public-home feed; still protected by the demo confirmation guard."""
    return {'demo_mode': True, 'quote_currency': 'USD',
            'assets': provider.get_landing_assets()}

@router.get('/live')
def live_prices(provider: Provider):
    return {'demo_mode': True, 'quote_currency': 'USDT',
            'assets': [provider.get_ticker(symbol).model_dump(mode='json') for symbol in CURRENCIES]}

@router.get('/candles/{symbol}')
def candles(symbol: str, provider: Provider, interval: str = '1h', limit: int = 100):
    try:
        rows = provider.get_candles(symbol, interval, limit)
        return {'demo_mode': True, 'symbol': symbol.upper(), 'interval': interval,
                'candles': [row.model_dump(mode='json') if hasattr(row, 'model_dump') else row for row in rows]}
    except ValueError as exc:
        raise HTTPException(422, str(exc))

@router.get('/ticker/{symbol}', response_model=Ticker)
def ticker(symbol: str, provider: Provider):
    try: return provider.get_ticker(symbol)
    except ValueError: raise HTTPException(422, 'Unsupported asset')
