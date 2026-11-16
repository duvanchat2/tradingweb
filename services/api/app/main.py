from contextlib import asynccontextmanager
import asyncio
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from sqlalchemy import text
from redis.exceptions import RedisError
from app.core.config import get_settings
from app.core.db import engine, SessionLocal
from app.routers.auth import router, get_redis
from app.routers.market import router as market_router
from app.routers.trading import router as trading_router
from app.admin.router import router as admin_router
from app.services.marketdata import get_market_provider, MarketDataUnavailable
from app.services.ledger import LedgerError
from app.services.order_worker import run_limit_worker

settings = get_settings()  # Fail closed before serving requests.
@asynccontextmanager
async def lifespan(app):
    stop = asyncio.Event()
    task = asyncio.create_task(run_limit_worker(stop,SessionLocal,get_market_provider())) if settings.limit_worker_enabled else None
    try:
        yield
    finally:
        stop.set()
        if task: await task
        if get_market_provider.cache_info().currsize:
            get_market_provider().close()
            get_market_provider.cache_clear()
        get_redis().close()
        engine.dispose()

app = FastAPI(title='Tradingweb Demo API', version='0.1.0', lifespan=lifespan)
app.include_router(router)
app.include_router(market_router)
app.include_router(trading_router)
app.include_router(admin_router)

@app.exception_handler(LedgerError)
async def ledger_error(request, exc):
    return JSONResponse(status_code=422,content={'detail':str(exc)})

@app.exception_handler(MarketDataUnavailable)
async def market_unavailable(request, exc):
    return JSONResponse(status_code=503,content={'detail':str(exc)})

@app.middleware('http')
async def demo_confirmation(request: Request, call_next):
    if (request.url.path == '/api' or request.url.path.startswith('/api/')) and request.headers.get('X-Demo-Confirm') != 'true':
        return JSONResponse(status_code=428, content={'detail':'X-Demo-Confirm: true required; virtual funds only'})
    try:
        response = await call_next(request)
    except RedisError:
        return JSONResponse(status_code=503, content={'detail':'Session service unavailable'})
    response.headers['X-Demo-Mode'] = 'true'
    return response

@app.get('/api/meta')
def meta(): return {'demo_mode':True, 'message':'Entorno de simulación'}

@app.get('/healthz')
def health():
    with engine.connect() as db: db.execute(text('SELECT 1'))
    get_redis().ping()
    return {'status':'ok','demo_mode':True}
