from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from sqlalchemy import text
from redis.exceptions import RedisError
from app.core.config import get_settings
from app.core.db import engine
from app.routers.auth import router, get_redis

settings = get_settings()  # Fail closed before serving requests.
@asynccontextmanager
async def lifespan(app):
    yield
    get_redis().close()
    engine.dispose()

app = FastAPI(title='Tradingweb Demo API', version='0.1.0', lifespan=lifespan)
app.include_router(router)

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
