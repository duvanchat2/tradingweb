# Tradingweb VPS deployment

Deployed on 2026-11-15 to `62.84.186.32` from `duvanchat2/tradingweb` `main` at commit `6942c11`.

## Architecture

- Existing Nginx remains the only public listener on ports 80 and 443 and terminates TLS.
- Tradingweb Caddy is HTTP-only and bound to `127.0.0.1:8180`.
- API is additionally bound to `127.0.0.1:8100` for local diagnostics.
- PostgreSQL and Redis have no host-published ports and are reachable only on `tradingweb_default`.
- All Docker resources use `COMPOSE_PROJECT_NAME=tradingweb`.

Routes:

- `api.globalcomercehub.xyz` -> Nginx -> Caddy -> `api:8000`
- `app.globalcomercehub.xyz` -> Nginx -> Caddy -> `web:3000`; `/` redirects 307 to `/app`
- `admin.globalcomercehub.xyz` -> Caddy -> `admin:3000`; `/` redirects 307 to `/admin` after DNS and TLS are enabled

## Changes made

- Created `/etc/nginx/sites-available/tradingweb.conf`.
- Created `/etc/nginx/sites-enabled/tradingweb.conf` as a symlink to that file.
- Certbot modified only this new vhost to add HTTPS and HTTP-to-HTTPS redirects.
- Issued one Let's Encrypt certificate containing three DNS names: `api.globalcomercehub.xyz`, `app.globalcomercehub.xyz`, and `admin.globalcomercehub.xyz`. Certbot reports expiry `2027-02-13` and installed automatic renewal.
- Updated `infra/caddy/Caddyfile` for the three real Host headers and the web/admin base-path redirects.
- Added `/backups/` to `.gitignore` so database and environment backups cannot be accidentally committed.
- Generated `infra/.env` locally on the VPS with mode 600. It is Git-ignored and was not committed.
- Created Docker network `tradingweb_default`, volumes prefixed `tradingweb_`, and six containers prefixed `tradingweb-`.
- Added `/root/webtrading/scripts/backup-vps.sh` and the root cron entry shown below.
- Created `docs/VPS_INVENTORY_POST.md` and `docs/VPS_INVENTORY_COMPARISON.md`.

Root cron:

```cron
15 3 * * * /root/webtrading/scripts/backup-vps.sh >> /var/log/tradingweb-backup.log 2>&1 # tradingweb-daily-backup
```

The backup writes a compressed `pg_dump`, a mode-600 copy of `.env`, and a mode-600 copy of the Caddyfile to `/root/webtrading/backups/`. Files older than seven days are deleted only when their names match the `tradingweb-*` backup patterns. A backup run was completed successfully during deployment.

## Verification

```text
GET https://api.globalcomercehub.xyz/healthz
{"status":"ok","demo_mode":true}

GET https://api.globalcomercehub.xyz/api/meta with X-Demo-Confirm: true
{"demo_mode":true,"message":"Entorno de simulación"}

HEAD https://app.globalcomercehub.xyz
HTTP/2 307

scripts/smoke.sh
PASS: curl register (201), login, me, refresh, logout (204), revoked session (401), demo confirmation (428)
```

Compose exposes only:

```text
127.0.0.1:8100 -> api:8000
127.0.0.1:8180 -> caddy:80
```

PostgreSQL and Redis expose only their container-network ports; neither publishes a host port.

## What was not changed

No existing Nginx vhost file, certificate, Docker container, network, volume, application directory, or cron entry was removed or edited. The only exception to the no-touch rule is the new Tradingweb Nginx file and its symlink. Certbot edits were confined to that new file.

Evidence is in:

- `docs/VPS_INVENTORY.md`: pre-deploy raw inventory.
- `docs/VPS_INVENTORY_POST.md`: post-deploy raw inventory.
- `docs/VPS_INVENTORY_COMPARISON.md`: normalized comparison.

The comparison reports no missing pre-existing container and no missing pre-existing listening address. The only new listeners are `127.0.0.1:8100` and `127.0.0.1:8180`. Existing applications including Multica, Socialdrop, OpenClaw, Genix Voice, Supabase, NocoDB, n8n, and WA Bridge retain their pre-deploy container states and ports. One OpenClaw sandbox container was already exited in the pre-deploy inventory and remains an unchanged pre-existing state.

## Admin hostname

`admin.globalcomercehub.xyz` resolves to `62.84.186.32`. The existing certificate was expanded successfully and now covers `api`, `app`, and `admin`. The admin root returns HTTP 307 to `/admin`.

## Rollback

Warning: `docker compose down -v` permanently removes the Tradingweb database and other Tradingweb volumes. Preserve `/root/webtrading/backups/` before running it.

```bash
cd /root/webtrading/infra
COMPOSE_PROJECT_NAME=tradingweb docker compose down -v

crontab -l | grep -v '# tradingweb-daily-backup' | crontab -

rm /etc/nginx/sites-enabled/tradingweb.conf
rm /etc/nginx/sites-available/tradingweb.conf
nginx -t
systemctl reload nginx

certbot delete --cert-name api.globalcomercehub.xyz
```

Optionally remove only Tradingweb images after the containers are down:

```bash
docker image rm tradingweb-api tradingweb-web tradingweb-admin
```

The repository and backups are deliberately not deleted by rollback. Remove them only after separately confirming they are no longer needed.

## Restore database

Create the Compose resources again, then restore a selected dump:

```bash
cd /root/webtrading/infra
COMPOSE_PROJECT_NAME=tradingweb docker compose up -d postgres redis
zcat /root/webtrading/backups/tradingweb-db-YYYYMMDDTHHMMSSZ.sql.gz | \
  COMPOSE_PROJECT_NAME=tradingweb docker compose exec -T postgres \
  psql -U "$POSTGRES_USER" "$POSTGRES_DB"
```
