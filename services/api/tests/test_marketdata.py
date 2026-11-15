from decimal import Decimal
import httpx
import pytest
from app.services.marketdata import BinanceTestnetProvider,MarketDataUnavailable

@pytest.fixture
def quote_provider(cache):
    state={'calls':0,'fail':False}
    def serve(request):
        state['calls']+=1
        assert request.method=='GET'
        assert request.url.params['symbol']=='BTCUSDT'
        if state['fail']: return httpx.Response(503)
        return httpx.Response(200,json={'price':'123.45','lastPrice':'123.45',
            'priceChangePercent':'-1','highPrice':'130','lowPrice':'120','volume':'50'})
    client=httpx.Client(base_url='https://api.binance.com',transport=httpx.MockTransport(serve))
    provider=BinanceTestnetProvider(cache,client)
    yield provider,state
    provider.close()

def test_price_cache_rate_and_five_second_ttl(quote_provider,cache):
    provider,state=quote_provider
    assert provider.get_price('BTC')==Decimal('123.45')
    assert provider.get_price('BTCUSDT')==Decimal('123.45')
    assert state['calls']==1
    assert 0<cache.ttl('market:binance:price:BTC')<=5
    cache.delete('market:binance:price:BTC')
    provider.get_price('BTC')
    assert state['calls']==2

def test_ticker_cache_and_shape(quote_provider,cache):
    provider,state=quote_provider
    ticker=provider.get_ticker('BTC')
    assert ticker.change_percent_24h==Decimal('-1')
    assert ticker.high_24h==130 and not ticker.stale
    assert provider.get_ticker('BTC').price==ticker.price
    assert state['calls']==1
    assert 0<cache.ttl('market:binance:ticker:BTC')<=5

def test_circuit_breaker_opens_after_three_failures_and_falls_back(quote_provider,cache):
    provider,state=quote_provider
    provider.get_price('BTC')
    cache.delete('market:binance:price:BTC')
    state['fail']=True
    for _ in range(3): assert provider.get_price('BTC')==Decimal('123.45')
    assert state['calls']==4
    assert 0<cache.ttl('market:binance:circuit')<=60
    assert provider.get_price('BTC')==Decimal('123.45')
    assert state['calls']==4
    cache.delete('market:binance:circuit') # deterministic cooldown expiry
    state['fail']=False
    provider.get_price('BTC')
    assert state['calls']==5
    assert not cache.exists('market:binance:failures')

def test_ticker_fallback_marks_stale(quote_provider,cache):
    provider,state=quote_provider
    provider.get_ticker('BTC');cache.delete('market:binance:ticker:BTC')
    state['fail']=True
    assert provider.get_ticker('BTC').stale

def test_no_price_is_invented_when_upstream_is_unavailable(quote_provider,cache):
    provider,state=quote_provider;state['fail']=True
    for _ in range(3):
        with pytest.raises(MarketDataUnavailable): provider.get_price('BTC')
    with pytest.raises(MarketDataUnavailable): provider.get_price('BTC')
    assert state['calls']==3

def test_success_resets_consecutive_failure_count(quote_provider,cache):
    provider,state=quote_provider;state['fail']=True
    with pytest.raises(MarketDataUnavailable):provider.get_price('BTC')
    assert cache.get('market:binance:failures')=='1'
    state['fail']=False;provider.get_price('BTC')
    assert not cache.exists('market:binance:failures')

def test_usdt_numeraire_does_not_call_upstream(quote_provider):
    provider,state=quote_provider
    assert provider.get_price('USDT')==1
    assert provider.get_ticker('USDT').source=='USDT-numeraire'
    with pytest.raises(ValueError):provider.get_price('UNSUPPORTED')
    assert state['calls']==0

def test_public_market_endpoints_use_fake_and_demo_guard(client):
    response=client.get('/api/market/prices')
    assert response.status_code==200 and len(response.json()['prices'])==9
    assert client.get('/api/market/ticker/BTC').json()['source']=='integration-fixture'
    assert client.get('/api/market/ticker/NOPE').status_code==422
    client.headers.pop('X-Demo-Confirm')
    assert client.get('/api/market/prices').status_code==428
