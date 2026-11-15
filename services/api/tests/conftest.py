import os
import secrets
import pytest
from fastapi.testclient import TestClient
from redis import Redis
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Tests require a dedicated PostgreSQL database and a separate Redis namespace.
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
def client(db, cache):
    app.dependency_overrides[get_db] = lambda: db
    app.dependency_overrides[get_redis] = lambda: cache
    with TestClient(app, headers={'X-Demo-Confirm':'true'}) as client:
        yield client
    app.dependency_overrides.clear()
