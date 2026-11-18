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

class Candle(BaseModel):
    open_time: int
    close_time: int
    open: Decimal
    high: Decimal
    low: Decimal
    close: Decimal
    volume: Decimal

class MarketDataProvider(Protocol):
    def get_price(self, symbol: str) -> Decimal: ...
    def get_ticker(self, symbol: str) -> Ticker: ...
    def get_landing_assets(self) -> list[dict]: ...
    def get_candles(self, symbol: str, interval: str = '1h', limit: int = 100) -> list[Candle]: ...

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
    def __init__(self, cache: Redis, client: httpx.Client | None = None,
                 landing_client: httpx.Client | None = None, api_key: str | None = None):
        self.cache = cache
        self.client = client or httpx.Client(base_url='https://api.binance.com', timeout=3.0, follow_redirects=False)
        self.landing_client = landing_client or httpx.Client(base_url='https://api.coingecko.com/api/v3', timeout=5.0, follow_redirects=False)
        self.api_key = api_key

    def close(self):
        self.client.close()
        self.landing_client.close()

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

    def get_candles(self, symbol: str, interval: str = '1h', limit: int = 100) -> list[Candle]:
        symbol = normalize_symbol(symbol)
        allowed = {'1m','5m','15m','1h','4h','1d'}
        if interval not in allowed: raise ValueError('Unsupported candle interval')
        if limit < 1 or limit > 500: raise ValueError('Candle limit must be between 1 and 500')
        if symbol == 'USDT':
            now = int(datetime.now(timezone.utc).timestamp() * 1000)
            return [Candle(open_time=now, close_time=now, open=1, high=1, low=1, close=1, volume=0)]
        key = f'{self.prefix}candles:{symbol}:{interval}:{limit}'
        raw = self.cache.get(key)
        if raw: return [Candle(**item) for item in json.loads(raw)]
        try:
            response = self.client.get('/api/v3/klines', params={
                'symbol': symbol+'USDT', 'interval': interval, 'limit': limit,
            })
            response.raise_for_status()
            candles = [Candle(open_time=row[0], close_time=row[6], open=row[1], high=row[2],
                              low=row[3], close=row[4], volume=row[5]) for row in response.json()]
            if not candles: raise ValueError('Empty candle response')
        except (httpx.HTTPError, ValueError, KeyError, TypeError, IndexError, InvalidOperation):
            raise MarketDataUnavailable('Candle data unavailable')
        self.cache.set(key, json.dumps([item.model_dump(mode='json') for item in candles]), ex=15)
        return candles

    def get_landing_assets(self) -> list[dict]:
        """One CoinGecko batch cached for five minutes; never exposes the key."""
        cache_key = self.prefix + 'landing:v1'
        raw = self.cache.get(cache_key)
        if raw:
            return json.loads(raw)
        ids = {
            'bitcoin':'BTC','ethereum':'ETH','tether':'USDT','binancecoin':'BNB',
            'usd-coin':'USDC','ripple':'XRP','solana':'SOL','tron':'TRX','dogecoin':'DOGE',
        }
        headers = {'x-cg-demo-api-key': self.api_key} if self.api_key else {}
        try:
            response = self.landing_client.get('/coins/markets', params={
                'vs_currency':'usd', 'ids':','.join(ids),
                'price_change_percentage':'24h', 'sparkline':'false',
            }, headers=headers)
            response.raise_for_status()
            by_symbol = {ids[item['id']]: item for item in response.json() if item.get('id') in ids}
            assets = []
            for symbol in ids.values():
                item = by_symbol[symbol]
                assets.append({
                    'symbol':symbol, 'price':str(item['current_price']),
                    'change_percent_24h':str(item.get('price_change_percentage_24h') or 0),
                    'market_cap':str(item.get('market_cap')) if item.get('market_cap') is not None else None,
                    'observed_at':item.get('last_updated'), 'stale':False, 'source':'coingecko',
                })
            if len(assets) != len(ids):
                raise ValueError('Incomplete CoinGecko response')
            encoded = json.dumps(assets)
            with self.cache.pipeline() as pipe:
                pipe.set(cache_key, encoded, ex=300)
                pipe.set(cache_key+':last', encoded, ex=86400)
                pipe.execute()
            return assets
        except (httpx.HTTPError, ValueError, KeyError, TypeError):
            last = self.cache.get(cache_key+':last')
            if last:
                assets = json.loads(last)
                for asset in assets: asset['stale'] = True
                return assets
            assets = []
            for symbol in ids.values():
                ticker = self.get_ticker(symbol)
                assets.append({
                    'symbol':symbol, 'price':str(ticker.price),
                    'change_percent_24h':str(ticker.change_percent_24h),
                    'market_cap':None, 'observed_at':ticker.observed_at.isoformat(),
                    'stale':ticker.stale, 'source':ticker.source,
                })
            return assets

@lru_cache
def get_market_provider() -> BinanceTestnetProvider:
    from app.core.config import get_settings
    return BinanceTestnetProvider(get_redis(), api_key=get_settings().coingecko_api_key)
