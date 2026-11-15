"""Explicit opt-in curl harness; cannot start against the normal demo database."""
from app.main import app,settings
from app.services.marketdata import get_market_provider
from tests.fakes import FakeMarketDataProvider

def create_app():
    if not settings.database_url.endswith('/tradingweb_smoke_test'):
        raise RuntimeError('Curl harness requires isolated tradingweb_smoke_test database')
    if not settings.redis_url.endswith('/14') or settings.limit_worker_enabled:
        raise RuntimeError('Curl harness requires Redis DB 14 and disabled background worker')
    app.dependency_overrides[get_market_provider]=lambda:FakeMarketDataProvider()
    return app
