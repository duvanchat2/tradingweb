# VPS Inventory Comparison

Compared (UTC): 2026-11-15T15:58:29Z

## Missing pre-existing containers
```text
```

An empty block means every container present before deployment still exists.

## New containers
```text
tradingweb-admin-1
tradingweb-api-1
tradingweb-caddy-1
tradingweb-postgres-1
tradingweb-redis-1
tradingweb-web-1
```

## Missing pre-existing listening addresses
```text
```

An empty block means every address/port present before deployment is still listening.

## New listening addresses
```text
127.0.0.1:8100
127.0.0.1:8180
```

## Pre-existing container status after deployment
```text
genix-voice-agent-1|Up 25 hours|
genix-voice-dispatcher-1|Up 25 hours|
genix-voice-livekit-1|Up 25 hours|
genix-voice-redis-1|Up 25 hours (healthy)|
genix-voice-sip-1|Up 25 hours|
multica-backend-1|Up 25 hours|127.0.0.1:8090->8080/tcp
multica-frontend-1|Up 25 hours|127.0.0.1:3020->3000/tcp
multica-postgres-1|Up 25 hours (healthy)|5432/tcp
multica-redis-1|Up 25 hours|6379/tcp
n8n|Up 25 hours|0.0.0.0:5678->5678/tcp, [::]:5678->5678/tcp
n8n-postgres|Up 25 hours (healthy)|5432/tcp
nocodb-nocodb-1|Up 25 hours|127.0.0.1:8095->8080/tcp
openclaw|Up 25 hours|
openclaw-sbx-agent-main-f331f052|Exited (255) 6 months ago|
realtime-dev.supabase-realtime|Up 25 hours (healthy)|
socialdrop-postgres|Up 25 hours (healthy)|5432/tcp
socialdrop-redis|Up 25 hours|6379/tcp
supabase-auth|Up 25 hours (healthy)|
supabase-db|Up 25 hours (healthy)|5432/tcp
supabase-edge-functions|Up 25 hours (healthy)|
supabase-envoy|Up 25 hours (healthy)|127.0.0.1:8000->8000/tcp, 10000/tcp
supabase-imgproxy|Up 25 hours (healthy)|8080/tcp
supabase-meta|Up 25 hours (healthy)|8080/tcp
supabase-pooler|Up 25 hours (healthy)|127.0.0.1:6543->6543/tcp, 127.0.0.1:54322->5432/tcp
supabase-rest|Up 25 hours (healthy)|3000/tcp
supabase-storage|Up 25 hours (healthy)|5000/tcp
supabase-studio|Up 25 hours (healthy)|3000/tcp
wa-bridge|Up 25 hours|127.0.0.1:8080->8080/tcp
```
