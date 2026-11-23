from datetime import date, datetime, timezone
from zoneinfo import ZoneInfo
import hashlib, hmac
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
from app.models.schema import User, Account, AuditLog, Office

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
    registration_code: str | None = Field(default=None, min_length=6, max_length=6, pattern=r'^[A-Z]{3}[0-9]{3}$')
class RefreshBody(BaseModel):
    refresh_token: str
class PasswordChange(BaseModel):
    current_password: str
    new_password: str = Field(min_length=12, max_length=128)
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

def issue_pair(user, cache, sid=None, request=None):
    sid = sid or str(uuid4())
    access, _ = token(user, 'access', sid)
    refresh, claims = token(user, 'refresh', sid)
    cache.set('session:'+sid, str(user.id), ex=seconds(get_settings().refresh_token_ttl))
    if request is not None:
        cache.hset('session-meta:'+sid, mapping={'user_id':str(user.id),'agent':request.headers.get('user-agent','Unknown')[:240], 'ip':request.client.host if request.client else '', 'created_at':datetime.now(timezone.utc).isoformat()})
        cache.expire('session-meta:'+sid, seconds(get_settings().refresh_token_ttl))
        cache.sadd('user-sessions:'+str(user.id), sid)
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

def current_registration_code(office: Office, day: date | None = None) -> str:
    local_day = day or datetime.now(ZoneInfo('America/Bogota')).date()
    digest = hmac.new(office.token_secret.encode(), local_day.isoformat().encode(), hashlib.sha256).digest()
    return ''.join(chr(ord('A') + value % 26) for value in digest[:3]) + ''.join(str(value % 10) for value in digest[3:6])

@router.post('/register', response_model=UserOut, status_code=201)
def register(body: Registration, db: DB):
    office = None
    if body.registration_code:
        code = body.registration_code.upper()
        office = next((candidate for candidate in db.scalars(select(Office).where(Office.is_active.is_(True))).all()
                       if hmac.compare_digest(current_registration_code(candidate), code)), None)
        if office is None: raise HTTPException(422, 'Office registration code is invalid or expired')
    user = User(email=body.email, password_hash=hasher.hash(body.password), full_name=body.full_name,
                country=body.country, phone=body.phone, registration_code=body.registration_code,
                office_id=office.id if office else None, role='client')
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
    return issue_pair(user, cache, request=request)

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
    cache.delete('session-meta:'+claims['sid'])
    cache.srem('user-sessions:'+str(user.id), claims['sid'])

def session_rows(user, cache, current_sid):
    rows=[]
    for sid in cache.smembers('user-sessions:'+str(user.id)):
        if cache.get('session:'+sid) != str(user.id):
            cache.srem('user-sessions:'+str(user.id),sid)
            continue
        meta=cache.hgetall('session-meta:'+sid)
        rows.append({'id':sid,'agent':meta.get('agent','Unknown'),'ip':meta.get('ip',''),'created_at':meta.get('created_at'),'current':sid==current_sid})
    return sorted(rows,key=lambda row:row['created_at'] or '',reverse=True)

@router.get('/sessions')
def sessions(user: Annotated[User, Depends(current_user)], cache: Cache, credentials: Annotated[HTTPAuthorizationCredentials, Depends(bearer)]):
    return {'items':session_rows(user,cache,decode(credentials.credentials,'access')['sid'])}

@router.delete('/sessions/{sid}')
def revoke_session(sid: str, user: Annotated[User, Depends(current_user)], cache: Cache, credentials: Annotated[HTTPAuthorizationCredentials, Depends(bearer)]):
    current_sid=decode(credentials.credentials,'access')['sid']
    if sid==current_sid: raise HTTPException(422,'Use logout for the current session')
    if sid not in cache.smembers('user-sessions:'+str(user.id)): raise HTTPException(404,'Session not found')
    cache.delete('session:'+sid,'session-meta:'+sid)
    cache.srem('user-sessions:'+str(user.id),sid)
    return {'revoked':True}

@router.post('/sessions/revoke-others')
def revoke_others(user: Annotated[User, Depends(current_user)], cache: Cache, credentials: Annotated[HTTPAuthorizationCredentials, Depends(bearer)]):
    current_sid=decode(credentials.credentials,'access')['sid']
    for row in session_rows(user,cache,current_sid):
        if not row['current']:
            cache.delete('session:'+row['id'],'session-meta:'+row['id'])
            cache.srem('user-sessions:'+str(user.id),row['id'])
    return {'revoked':True}

@router.post('/password')
def change_password(body: PasswordChange, user: Annotated[User, Depends(current_user)], db: DB, cache: Cache, credentials: Annotated[HTTPAuthorizationCredentials, Depends(bearer)]):
    if not verify_password(body.current_password,user.password_hash): raise HTTPException(401,'Current password is incorrect')
    if body.current_password==body.new_password: raise HTTPException(422,'Choose a different password')
    user.password_hash=hasher.hash(body.new_password)
    db.add(AuditLog(actor_id=user.id,action='auth.password_change',entity='users',entity_id=user.id))
    db.commit()
    revoke_others(user,cache,credentials)
    return {'changed':True}

@router.get('/me', response_model=UserOut)
def me(user: Annotated[User, Depends(current_user)]): return user
