"""Public market reads only. No exchange account, credentials, or execution API."""
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation
from functools import lru_cache
from typing import Protocol
import json
import httpx
from pydantic import BaseModel
from redis import Redis
from app.routers.auth import CURRENCIES, get_redis

class MarketDataUnavailable(RuntimeError): pass

class Ticker(BaseModel):
    symbol: str
    price: Decimal
    change_percent_24h: Decimal = Decimal('0')
    high_24h: Decimal
    low_24h: Decimal
    volume_24h: Decimal = Decimal('0')
    observed_at: datetime
    stale: bool = False
    source: str = 'binance-public'

class MarketDataProvider(Protocol):
    def get_price(self, symbol: str) -> Decimal: ...
    def get_ticker(self, symbol: str) -> Ticker: ...

def normalize_symbol(symbol: str) -> str:
    symbol = symbol.upper()
    if symbol.endswith('USDT') and symbol != 'USDT': symbol = symbol[:-4]
    if symbol not in CURRENCIES: raise ValueError('Unsupported asset')
    return symbol

class BinanceTestnetProvider:
    """Name retained from spec; URL is Binance PUBLIC spot market data, not testnet.

    Only fixed GET ticker endpoints are available. Redis shares the circuit state
    across API processes. A successful network response resets the failure count.
    """
    prefix = 'market:binance:'
    def __init__(self, cache: Redis, client: httpx.Client | None = None):
        self.cache = cache
        self.client = client or httpx.Client(base_url='https://api.binance.com', timeout=3.0, follow_redirects=False)

    def close(self): self.client.close()

    def _fallback(self, symbol, kind):
        raw = self.cache.get(self.prefix+'last:'+kind+':'+symbol)
        if raw:
            value = json.loads(raw)
            value['stale'] = True
            return value
        # A cached ticker can also supply the last price when /price is unavailable.
        if kind == 'price':
            raw = self.cache.get(self.prefix+'last:ticker:'+symbol)
            if raw:
                value = json.loads(raw)
                value['stale'] = True
                return value
        raise MarketDataUnavailable('Market data unavailable and no last-known quote exists')

    def _read(self, symbol: str, kind: str):
        symbol = normalize_symbol(symbol)
        if symbol == 'USDT':
            return {'symbol':'USDT','price':'1','high_24h':'1','low_24h':'1',
                    'observed_at':datetime.now(timezone.utc).isoformat(),'source':'USDT-numeraire'}
        key = self.prefix+kind+':'+symbol
        raw = self.cache.get(key)
        if raw: return json.loads(raw)
        if self.cache.exists(self.prefix+'circuit'):
            return self._fallback(symbol, kind)
        try:
            path = '/api/v3/ticker/price' if kind == 'price' else '/api/v3/ticker/24hr'
            response = self.client.get(path, params={'symbol':symbol+'USDT'})
            response.raise_for_status()
            raw_data = response.json()
            price = Decimal(raw_data['price' if kind == 'price' else 'lastPrice'])
            if not price.is_finite() or price <= 0: raise ValueError('Invalid quote')
            value = {'symbol':symbol,'price':str(price),'observed_at':datetime.now(timezone.utc).isoformat()}
            if kind == 'ticker':
                for name, upstream in [('change_percent_24h','priceChangePercent'),('high_24h','highPrice'),('low_24h','lowPrice'),('volume_24h','volume')]:
                    number = Decimal(raw_data[upstream])
                    if not number.is_finite() or (name != 'change_percent_24h' and number < 0):
                        raise ValueError('Invalid ticker')
                    value[name] = str(number)
        except (httpx.HTTPError, ValueError, KeyError, TypeError, InvalidOperation):
            # Increment and open the circuit atomically; no retry storm across workers.
            self.cache.eval("""
                local failures = redis.call('INCR', KEYS[1])
                if failures >= 3 then
                    redis.call('SET', KEYS[2], 'open', 'EX', 60)
                    redis.call('DEL', KEYS[1])
                end
                return failures
            """, 2, self.prefix+'failures', self.prefix+'circuit')
            return self._fallback(symbol, kind)
        encoded = json.dumps(value)
        with self.cache.pipeline() as pipe:
            pipe.set(key, encoded, ex=5)
            pipe.set(self.prefix+'last:'+kind+':'+symbol, encoded)
            pipe.delete(self.prefix+'failures')
            pipe.execute()
        return value

    def get_price(self, symbol: str) -> Decimal:
        return Decimal(self._read(symbol, 'price')['price'])

    def get_ticker(self, symbol: str) -> Ticker:
        return Ticker(**self._read(symbol, 'ticker'))

@lru_cache
def get_market_provider() -> BinanceTestnetProvider:
    return BinanceTestnetProvider(get_redis())
