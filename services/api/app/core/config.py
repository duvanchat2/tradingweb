from functools import lru_cache
from pydantic import Field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env', extra='ignore')
    database_url: str
    redis_url: str
    demo_mode: bool = True
    limit_worker_enabled: bool = True
    live_license_key: str | None = None
    jwt_secret: str = Field(min_length=32)
    jwt_alg: str = 'HS256'
    access_token_ttl: str = '15m'
    refresh_token_ttl: str = '7d'
    seed_password: str = Field(min_length=12)

    @model_validator(mode='after')
    def validate_mode(self):
        if not self.demo_mode:
            raise ValueError('Only DEMO_MODE=true is supported; live operation is not implemented (even with LIVE_LICENSE_KEY).')
        if self.jwt_alg != 'HS256':
            raise ValueError('Only HS256 is supported')
        for value in (self.access_token_ttl, self.refresh_token_ttl):
            if len(value) < 2 or value[-1] not in 'smhd' or not value[:-1].isdigit() or int(value[:-1]) <= 0:
                raise ValueError('Token TTL must be a positive duration, e.g. 15m or 7d')
        return self

@lru_cache
def get_settings():
    return Settings()

def seconds(value: str) -> int:
    return int(value[:-1]) * {'s':1, 'm':60, 'h':3600, 'd':86400}[value[-1]]
