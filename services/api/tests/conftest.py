import os
import secrets
import pytest
from fastapi.testclient import TestClient
from redis import Redis
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Tests require a dedicated PostgreSQL database and a separate Redis namespace.
os.environ['LIMIT_WORKER_ENABLED'] = 'false'
os.environ['DATABASE_URL'] = os.environ['TEST_DATABASE_URL']
os.environ['REDIS_URL'] = os.environ['TEST_REDIS_URL']
os.environ['JWT_SECRET'] = secrets.token_hex(32)
os.environ['SEED_PASSWORD'] = secrets.token_urlsafe(24)
from app.models.schema import Base
from app.core.db import get_db
from app.main import app
from app.routers.auth import get_redis

@pytest.fixture
def engine():
    url = os.environ['TEST_DATABASE_URL']
    if not url.split('/')[-1].endswith('_test'):
        raise RuntimeError('Refusing to reset a database not ending in _test')
    engine = create_engine(url)
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    yield engine
    Base.metadata.drop_all(engine)
    engine.dispose()

@pytest.fixture
def db(engine):
    with sessionmaker(engine,expire_on_commit=False)() as session:
        yield session
        session.rollback()

@pytest.fixture
def cache():
    redis = Redis.from_url(os.environ['TEST_REDIS_URL'],decode_responses=True)
    if redis.connection_pool.connection_kwargs['db'] != 15:
        raise RuntimeError('Tests require Redis database 15')
    redis.flushdb()
    yield redis
    redis.flushdb()
    redis.close()

@pytest.fixture
def client(db, cache, fake_provider):
    app.dependency_overrides[get_db] = lambda: db
    app.dependency_overrides[get_redis] = lambda: cache
    from app.services.marketdata import get_market_provider
    app.dependency_overrides[get_market_provider] = lambda: fake_provider
    with TestClient(app, headers={'X-Demo-Confirm':'true'}) as client:
        yield client
    app.dependency_overrides.clear()


@pytest.fixture(autouse=True)
def prohibit_real_market_network(monkeypatch):
    import httpx
    def blocked(*args, **kwargs):
        raise AssertionError('Real HTTP network is forbidden in pytest; use a fake or MockTransport')
    monkeypatch.setattr(httpx.HTTPTransport, 'handle_request', blocked)

@pytest.fixture
def fake_provider():
    from tests.fakes import FakeMarketDataProvider
    return FakeMarketDataProvider()

@pytest.fixture
def funded(db,client):
    from decimal import Decimal
    from app.models.schema import User,Account
    from app.services.ledger import post_entry
    from app.routers.auth import current_user,CURRENCIES
    owner=User(email='treasury@example.com',full_name='Demo treasury',password_hash='unused',role='superworker')
    user=User(email='trader@example.com',full_name='Trader',password_hash='unused')
    other=User(email='other@example.com',full_name='Other',password_hash='unused')
    db.add_all([owner,user,other]);db.flush()
    for currency in CURRENCIES:
        treasury=Account(user_id=owner.id,type='system',normal_side='credit',currency=currency)
        db.add(treasury);db.flush()
        for client_user in (user,other):
            account=Account(user_id=client_user.id,type='main',currency=currency)
            db.add(account);db.flush()
            post_entry(db,debit_account_id=treasury.id,credit_account_id=account.id,amount=Decimal('1000'))
    db.commit()
    app.dependency_overrides[current_user]=lambda:user
    return user,other,owner
