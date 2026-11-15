"""Deterministic quotes exclusively for tests and the isolated curl harness."""
from datetime import datetime,timezone
from decimal import Decimal
from app.services.marketdata import Ticker,normalize_symbol

class FakeMarketDataProvider:
    def __init__(self):
        self.prices={symbol:Decimal(value) for symbol,value in {
            'BTC':'100','ETH':'10','USDT':'1','USDC':'1','BNB':'5','XRP':'0.5','SOL':'2','TRX':'0.1','DOGE':'0.2'}.items()}
    def get_price(self,symbol):return self.prices[normalize_symbol(symbol)]
    def get_ticker(self,symbol):
        symbol=normalize_symbol(symbol);price=self.get_price(symbol)
        return Ticker(symbol=symbol,price=price,high_24h=price,low_24h=price,
                      observed_at=datetime.now(timezone.utc),source='integration-fixture')
