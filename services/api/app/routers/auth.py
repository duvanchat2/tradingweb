from datetime import datetime, timezone
from functools import lru_cache
from uuid import uuid4
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel, EmailStr, Field, field_validator
from redis import Redis
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from app.core.config import get_settings, seconds
from app.core.db import get_db
from app.core.security import hasher, verify_password, token, decode
from app.models.schema import User, Account, AuditLog

router = APIRouter(prefix='/api/auth', tags=['auth'])
bearer = HTTPBearer(auto_error=False)
CURRENCIES = ('BTC','ETH','USDT','USDC','BNB','XRP','SOL','TRX','DOGE')

@lru_cache
def get_redis(): return Redis.from_url(get_settings().redis_url, decode_responses=True)
DB = Annotated[Session, Depends(get_db)]
Cache = Annotated[Redis, Depends(get_redis)]
class Credentials(BaseModel):
    email: EmailStr
    password: str = Field(min_length=12, max_length=128)
    @field_validator('email')
    @classmethod
    def normalize_email(cls, value): return value.lower()
class Registration(Credentials):
    full_name: str = Field(min_length=1, max_length=200)
    country: str | None = Field(default=None, pattern=r'^[A-Z]{2}$')
    phone: str | None = Field(default=None, max_length=32)
    registration_code: str | None = Field(default=None, pattern=r'^[A-Z]{3}[0-9]{3}$')
class RefreshBody(BaseModel):
    refresh_token: str
class UserOut(BaseModel):
    model_config = {'from_attributes':True}
    id: int
    email: str
    full_name: str
    role: str
    kyc_status: str
    country: str | None
    phone: str | None
    registration_code: str | None
class Tokens(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = 'bearer'
    expires_in: int

def issue_pair(user, cache, sid=None):
    sid = sid or str(uuid4())
    access, _ = token(user, 'access', sid)
    refresh, claims = token(user, 'refresh', sid)
    cache.set('session:'+sid, str(user.id), ex=seconds(get_settings().refresh_token_ttl))
    cache.set('refresh:'+claims['jti'], sid, ex=seconds(get_settings().refresh_token_ttl))
    return Tokens(access_token=access, refresh_token=refresh, expires_in=seconds(get_settings().access_token_ttl))

def current_user(db: DB, cache: Cache, credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer)]):
    if credentials is None: raise HTTPException(401, 'Bearer token required')
    claims = decode(credentials.credentials, 'access')
    if cache.get('session:'+claims['sid']) != claims['sub']: raise HTTPException(401, 'Session revoked')
    user = db.get(User, int(claims['sub']))
    if not user or not user.is_active: raise HTTPException(401, 'Inactive user')
    return user

def require_staff(user: Annotated[User, Depends(current_user)], db: DB):
    if user.role not in ('staff','superworker'):
        db.add(AuditLog(actor_id=user.id,action='admin.denied',entity='authorization'))
        db.commit()
        raise HTTPException(403, 'Staff role required')
    return user

@router.post('/register', response_model=UserOut, status_code=201)
def register(body: Registration, db: DB):
    user = User(email=body.email, password_hash=hasher.hash(body.password), full_name=body.full_name,
                country=body.country, phone=body.phone, registration_code=body.registration_code, role='client')
    db.add(user)
    try:
        db.flush()
        db.add_all([Account(user_id=user.id, currency=c, type='main') for c in CURRENCIES])
        db.add(AuditLog(actor_id=user.id, action='auth.register', entity='users', entity_id=user.id))
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(409, 'Email already registered')
    return user

@router.post('/login', response_model=Tokens)
def login(body: Credentials, request: Request, db: DB, cache: Cache):
    key = 'login-attempts:'+(request.client.host if request.client else 'unknown')
    count = cache.incr(key)
    if count == 1: cache.expire(key, 60)
    if count > 20: raise HTTPException(429, 'Try again in one minute')
    user = db.scalar(select(User).where(User.email == body.email))
    if not user or not verify_password(body.password, user.password_hash) or not user.is_active:
        raise HTTPException(401, 'Invalid credentials')
    user.last_login_at = datetime.now(timezone.utc)
    user.last_login_ip = request.client.host if request.client else None
    db.add(AuditLog(actor_id=user.id, action='auth.login', entity='users', entity_id=user.id, ip=user.last_login_ip))
    db.commit()
    return issue_pair(user, cache)

@router.post('/refresh', response_model=Tokens)
def refresh(body: RefreshBody, db: DB, cache: Cache):
    claims = decode(body.refresh_token, 'refresh')
    sid = claims['sid']
    if cache.get('session:'+sid) != claims['sub']: raise HTTPException(401, 'Session revoked')
    user = db.get(User, int(claims['sub']))
    if not user or not user.is_active: raise HTTPException(401, 'Inactive user')
    access, _ = token(user, 'access', sid)
    new_refresh, new_claims = token(user, 'refresh', sid)
    # Consume and rotate in one Redis operation; logout cannot be undone by a race.
    rotated = cache.eval('''
        if redis.call('GET', KEYS[1]) ~= ARGV[1] then return 0 end
        if redis.call('GET', KEYS[2]) ~= ARGV[2] then
            redis.call('DEL', KEYS[1]); return 0
        end
        redis.call('DEL', KEYS[2])
        redis.call('SET', KEYS[3], ARGV[2], 'EX', ARGV[3])
        redis.call('EXPIRE', KEYS[1], ARGV[3])
        return 1
    ''', 3, 'session:'+sid, 'refresh:'+claims['jti'], 'refresh:'+new_claims['jti'],
        str(user.id), sid, seconds(get_settings().refresh_token_ttl))
    if not rotated: raise HTTPException(401, 'Refresh token reused or revoked')
    return Tokens(access_token=access, refresh_token=new_refresh, expires_in=seconds(get_settings().access_token_ttl))

@router.post('/logout', status_code=204)
def logout(user: Annotated[User, Depends(current_user)], cache: Cache, credentials: Annotated[HTTPAuthorizationCredentials, Depends(bearer)]):
    claims = decode(credentials.credentials, 'access')
    cache.delete('session:'+claims['sid'])

@router.get('/me', response_model=UserOut)
def me(user: Annotated[User, Depends(current_user)]): return user
