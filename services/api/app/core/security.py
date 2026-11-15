from datetime import datetime, timezone
from uuid import uuid4
import jwt
from argon2 import PasswordHasher
from argon2.exceptions import VerificationError, InvalidHashError
from fastapi import HTTPException
from app.core.config import get_settings, seconds
hasher = PasswordHasher()
def verify_password(password, hashed):
    try: return hasher.verify(hashed, password)
    except (VerificationError, InvalidHashError): return False

def token(user, token_type, sid):
    settings = get_settings()
    now = int(datetime.now(timezone.utc).timestamp())
    ttl = seconds(settings.access_token_ttl if token_type == 'access' else settings.refresh_token_ttl)
    claims = {'sub':str(user.id), 'type':token_type, 'sid':sid, 'jti':str(uuid4()), 'iat':now, 'exp':now+ttl, 'iss':'tradingweb-demo', 'aud':'tradingweb'}
    return jwt.encode(claims, settings.jwt_secret, algorithm=settings.jwt_alg), claims

def decode(value, expected_type):
    settings = get_settings()
    try:
        claims = jwt.decode(value, settings.jwt_secret, algorithms=[settings.jwt_alg], issuer='tradingweb-demo', audience='tradingweb', options={'require':['sub','type','sid','jti','iat','exp']})
        if claims['type'] != expected_type or not str(claims['sub']).isdigit(): raise ValueError()
        return claims
    except (jwt.PyJWTError, ValueError, TypeError):
        raise HTTPException(401, 'Invalid or expired token')
