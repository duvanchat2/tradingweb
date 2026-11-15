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

@router.get('/ticker/{symbol}', response_model=Ticker)
def ticker(symbol: str, provider: Provider):
    try: return provider.get_ticker(symbol)
    except ValueError: raise HTTPException(422, 'Unsupported asset')
