#!/bin/sh
set -eu
api_url="${API_URL:-http://127.0.0.1:8000}"
scratch_dir="$(mktemp -d)"
trap 'rm -rf "$scratch_dir"' EXIT HUP INT TERM
python3 - "$scratch_dir" <<'PY'
import json, secrets, sys
from pathlib import Path
p=Path(sys.argv[1])
body={'email':secrets.token_hex(8)+'@example.com','password':secrets.token_urlsafe(24)}
(p/'login.json').write_text(json.dumps(body))
(p/'register.json').write_text(json.dumps(dict(body,full_name='Curl Demo')))
PY
status="$(curl -sS -o "$scratch_dir/register.out" -w '%{http_code}' -H 'X-Demo-Confirm: true' -H 'Content-Type: application/json' --data-binary "@$scratch_dir/register.json" "$api_url/api/auth/register")"
[ "$status" = 201 ]
curl -fsS -H 'X-Demo-Confirm: true' -H 'Content-Type: application/json' --data-binary "@$scratch_dir/login.json" "$api_url/api/auth/login" > "$scratch_dir/tokens.json"
python3 - "$scratch_dir" <<'PY'
import json,sys
from pathlib import Path
p=Path(sys.argv[1]); tokens=json.loads((p/'tokens.json').read_text())
(p/'headers').write_text('X-Demo-Confirm: true\nAuthorization: Bearer '+tokens['access_token']+'\n')
(p/'refresh.json').write_text(json.dumps({'refresh_token':tokens['refresh_token']}))
PY
curl -fsS -H "@$scratch_dir/headers" "$api_url/api/auth/me" > "$scratch_dir/me.json"
curl -fsS -H 'X-Demo-Confirm: true' -H 'Content-Type: application/json' --data-binary "@$scratch_dir/refresh.json" "$api_url/api/auth/refresh" > "$scratch_dir/refreshed.json"
status="$(curl -sS -o /dev/null -w '%{http_code}' -X POST -H "@$scratch_dir/headers" "$api_url/api/auth/logout")"
[ "$status" = 204 ]
status="$(curl -sS -o /dev/null -w '%{http_code}' -H "@$scratch_dir/headers" "$api_url/api/auth/me")"
[ "$status" = 401 ]
status="$(curl -sS -o /dev/null -w '%{http_code}' "$api_url/api/meta")"
[ "$status" = 428 ]
printf '%s\n' 'PASS: curl register (201), login, me, refresh, logout (204), revoked session (401), demo confirmation (428)'
