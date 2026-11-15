"""Create local secrets without committing or printing them."""
from pathlib import Path
import secrets

root = Path(__file__).resolve().parent
target = root / '.env'
if target.exists():
    raise SystemExit('infra/.env already exists; preserved without changes')
values = (root / '.env.example').read_text()
for placeholder, value in {
    'REPLACE_WITH_RANDOM_URL_SAFE_VALUE': secrets.token_hex(20),
    'REPLACE_WITH_RANDOM_SECRET_AT_LEAST_32_CHARACTERS': secrets.token_hex(32),
    'REPLACE_WITH_DEVELOPMENT_PASSWORD': secrets.token_urlsafe(24),
}.items():
    values = values.replace(placeholder, value)
with target.open('x') as file:
    target.chmod(0o600)
    file.write(values)
print('Created infra/.env with local secrets. Demo passwords: SEED_PASSWORD in that file.')
