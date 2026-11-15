# VPS Inventory

Captured (UTC): 2026-11-15T15:41:42Z
Host: vmi2907731

## ss -tlnp
```text
State  Recv-Q Send-Q Local Address:Port  Peer Address:PortProcess
LISTEN 0      128          0.0.0.0:8081       0.0.0.0:*    users:(("python",pid=3012,fd=10))
LISTEN 0      4096       127.0.0.1:54322      0.0.0.0:*    users:(("docker-proxy",pid=3100,fd=8))
LISTEN 0      4096         0.0.0.0:7433       0.0.0.0:*    users:(("ruby",pid=8232,fd=9))
LISTEN 0      200        127.0.0.1:5432       0.0.0.0:*    users:(("postgres",pid=941,fd=7))
LISTEN 0      4096   127.0.0.53%lo:53         0.0.0.0:*    users:(("systemd-resolve",pid=667,fd=15))
LISTEN 0      511          0.0.0.0:7000       0.0.0.0:*    users:(("MainThread",pid=5063,fd=21))
LISTEN 0      4096       127.0.0.1:7880       0.0.0.0:*    users:(("livekit-server",pid=3826,fd=9))
LISTEN 0      4096       127.0.0.1:7681       0.0.0.0:*    users:(("ttyd",pid=696,fd=14))
LISTEN 0      4096       127.0.0.1:8080       0.0.0.0:*    users:(("docker-proxy",pid=4446,fd=8))
LISTEN 0      4096       127.0.0.1:8090       0.0.0.0:*    users:(("docker-proxy",pid=4072,fd=8))
LISTEN 0      4096       127.0.0.1:8095       0.0.0.0:*    users:(("docker-proxy",pid=3770,fd=8))
LISTEN 0      4096       127.0.0.1:8000       0.0.0.0:*    users:(("docker-proxy",pid=4593,fd=8))
LISTEN 0      4096         0.0.0.0:5678       0.0.0.0:*    users:(("docker-proxy",pid=3858,fd=8))
LISTEN 0      511        127.0.0.1:6379       0.0.0.0:*    users:(("redis-server",pid=708,fd=20))
LISTEN 0      511        127.0.0.1:6380       0.0.0.0:*    users:(("redis-server",pid=3756,fd=6))
LISTEN 0      4096       127.0.0.1:6543       0.0.0.0:*    users:(("docker-proxy",pid=3320,fd=8))
LISTEN 0      4096      127.0.0.54:53         0.0.0.0:*    users:(("systemd-resolve",pid=667,fd=17))
LISTEN 0      2048      172.17.0.1:8088       0.0.0.0:*    users:(("uvicorn",pid=3102,fd=6))
LISTEN 0      511        127.0.0.1:8799       0.0.0.0:*    users:(("MainThread",pid=1393,fd=31))
LISTEN 0      511        127.0.0.1:8800       0.0.0.0:*    users:(("MainThread",pid=1393,fd=30))
LISTEN 1      511          0.0.0.0:18789      0.0.0.0:*    users:(("openclaw-gatewa",pid=4791,fd=19))
LISTEN 0      128        127.0.0.1:8650       0.0.0.0:*    users:(("hermes",pid=1274,fd=16))
LISTEN 0      5          127.0.0.1:8651       0.0.0.0:*    users:(("python3",pid=1276,fd=3))
LISTEN 0      4096       127.0.0.1:19514      0.0.0.0:*    users:(("multica",pid=5062,fd=6))
LISTEN 0      2048         0.0.0.0:9119       0.0.0.0:*    users:(("hermes",pid=702,fd=9))
LISTEN 0      1024       127.0.0.1:3030       0.0.0.0:*    users:(("ruby",pid=693,fd=9))
LISTEN 0      4096       127.0.0.1:3020       0.0.0.0:*    users:(("docker-proxy",pid=3609,fd=8))
LISTEN 0      511        127.0.0.1:3000       0.0.0.0:*    users:(("MainThread",pid=2317,fd=21))
LISTEN 0      511          0.0.0.0:443        0.0.0.0:*    users:(("nginx",pid=3780058,fd=5),("nginx",pid=3780057,fd=5),("nginx",pid=3780056,fd=5),("nginx",pid=3780055,fd=5),("nginx",pid=3780054,fd=5),("nginx",pid=3780053,fd=5),("nginx",pid=1324,fd=5))
LISTEN 0      511          0.0.0.0:80         0.0.0.0:*    users:(("nginx",pid=3780058,fd=6),("nginx",pid=3780057,fd=6),("nginx",pid=3780056,fd=6),("nginx",pid=3780055,fd=6),("nginx",pid=3780054,fd=6),("nginx",pid=3780053,fd=6),("nginx",pid=1324,fd=6))
LISTEN 0      511        127.0.0.1:18791      0.0.0.0:*    users:(("openclaw-gatewa",pid=4791,fd=34))
LISTEN 0      4096         0.0.0.0:22         0.0.0.0:*    users:(("sshd",pid=2549,fd=3),("systemd",pid=1,fd=93))
LISTEN 0      4096               *:8089             *:*    users:(("livekit-sip",pid=2869,fd=10))
LISTEN 0      128             [::]:8081          [::]:*    users:(("python",pid=3012,fd=9))
LISTEN 0      4096               *:7881             *:*    users:(("livekit-server",pid=3826,fd=8))
LISTEN 0      4096            [::]:5678          [::]:*    users:(("docker-proxy",pid=3868,fd=8))
LISTEN 0      4096               *:5060             *:*    users:(("livekit-sip",pid=2869,fd=9))
LISTEN 0      200            [::1]:5432          [::]:*    users:(("postgres",pid=941,fd=6))
LISTEN 0      511                *:3010             *:*    users:(("PM2 v7.0.1: God",pid=1302,fd=44))
LISTEN 0      511                *:3011             *:*    users:(("next-server (v1",pid=1511,fd=21))
LISTEN 0      511                *:3001             *:*    users:(("next-server (v1",pid=1344,fd=22))
LISTEN 0      511                *:3002             *:*    users:(("PM2 v7.0.1: God",pid=1302,fd=24))
LISTEN 0      511            [::1]:6379          [::]:*    users:(("redis-server",pid=708,fd=21))
LISTEN 0      4096            [::]:22            [::]:*    users:(("sshd",pid=2549,fd=4),("systemd",pid=1,fd=94))
```

## docker ps -a
```text
CONTAINER ID   IMAGE                                       COMMAND                  CREATED         STATUS                      PORTS                                                 NAMES
d26b452e1fa5   nocodb/nocodb:2026.10.0                     "/usr/bin/dumb-init …"   3 days ago      Up 25 hours                 127.0.0.1:8095->8080/tcp                              nocodb-nocodb-1
8e0d3237f1b0   genix-voice-app:local                       "uvicorn voice_confi…"   3 days ago      Up 25 hours                                                                       genix-voice-dispatcher-1
28b4a36a49d0   genix-voice-app:local                       "python -m voice_con…"   3 days ago      Up 25 hours                                                                       genix-voice-agent-1
585a9af2accc   supabase/storage-api:v1.89.12               "docker-entrypoint.s…"   3 days ago      Up 25 hours (healthy)       5000/tcp                                              supabase-storage
d18319f5e6ae   supabase/edge-runtime:v1.77.9               "edge-runtime start …"   3 days ago      Up 25 hours (healthy)                                                             supabase-edge-functions
a3051a7553d6   supabase/realtime:v2.148.3                  "/usr/bin/tini -s -g…"   3 days ago      Up 25 hours (healthy)                                                             realtime-dev.supabase-realtime
1990bd026b1c   supabase/postgres-meta:v0.100.0             "docker-entrypoint.s…"   3 days ago      Up 25 hours (healthy)       8080/tcp                                              supabase-meta
ed3b99232003   supabase/supavisor:2.9.13                   "/usr/bin/tini -s -g…"   3 days ago      Up 25 hours (healthy)       127.0.0.1:6543->6543/tcp, 127.0.0.1:54322->5432/tcp   supabase-pooler
aaa075b29387   supabase/gotrue:v2.197.0                    "auth"                   3 days ago      Up 25 hours (healthy)                                                             supabase-auth
1a1fbc586586   postgrest/postgrest:v14.18                  "postgrest"              3 days ago      Up 25 hours (healthy)       3000/tcp                                              supabase-rest
c2902090ed76   envoyproxy/envoy:v1.39.6                    "/bin/sh /docker-ent…"   3 days ago      Up 25 hours (healthy)       127.0.0.1:8000->8000/tcp, 10000/tcp                   supabase-envoy
3a71cb5ce7e2   supabase/postgres:17.6.1.136                "docker-entrypoint.s…"   3 days ago      Up 25 hours (healthy)       5432/tcp                                              supabase-db
d6edf588bbe6   supabase/studio:2026.11.02-sha-a05e7ec      "docker-entrypoint.s…"   3 days ago      Up 25 hours (healthy)       3000/tcp                                              supabase-studio
34018b20ef5b   darthsim/imgproxy:v4.0.21                   "entrypoint.sh imgpr…"   3 days ago      Up 25 hours (healthy)       8080/tcp                                              supabase-imgproxy
d88eb116087e   livekit/sip:v1.18.0                         "livekit-sip --confi…"   2 weeks ago     Up 25 hours                                                                       genix-voice-sip-1
92e3693c540a   livekit/livekit-server:v1.13.9              "/livekit-server --c…"   2 weeks ago     Up 25 hours                                                                       genix-voice-livekit-1
565d37aeb11e   redis:7.4.10-alpine                         "docker-entrypoint.s…"   2 weeks ago     Up 25 hours (healthy)                                                             genix-voice-redis-1
1e6a1cd8dc24   docker.n8n.io/n8nio/n8n:2.9.4               "tini -- /docker-ent…"   7 weeks ago     Up 25 hours                 0.0.0.0:5678->5678/tcp, [::]:5678->5678/tcp           n8n
f5f49b385d6e   ghcr.io/multica-ai/multica-backend:latest   "./entrypoint.sh"        2 months ago    Up 25 hours                 127.0.0.1:8090->8080/tcp                              multica-backend-1
140d7d75c8d2   ghcr.io/multica-ai/multica-web:latest       "docker-entrypoint.s…"   2 months ago    Up 25 hours                 127.0.0.1:3020->3000/tcp                              multica-frontend-1
a6517ca88c96   redis:7-alpine                              "docker-entrypoint.s…"   2 months ago    Up 25 hours                 6379/tcp                                              multica-redis-1
e620ed5a985d   pgvector/pgvector:pg17                      "docker-entrypoint.s…"   2 months ago    Up 25 hours (healthy)       5432/tcp                                              multica-postgres-1
53ba363b6812   wa-bridge-wa-bridge                         "gunicorn --bind 0.0…"   7 months ago    Up 25 hours                 127.0.0.1:8080->8080/tcp                              wa-bridge
08036505cc9e   openclaw-openclaw                           "docker-entrypoint.s…"   7 months ago    Up 25 hours                                                                       openclaw
8a45389ed395   openclaw-sandbox:bookworm-slim              "sleep infinity"         7 months ago    Exited (255) 6 months ago                                                         openclaw-sbx-agent-main-f331f052
229bd814d4eb   postgres:17-alpine                          "docker-entrypoint.s…"   7 months ago    Up 25 hours (healthy)       5432/tcp                                              socialdrop-postgres
c3faa69da5a0   8b81dd37ff02                                "docker-entrypoint.s…"   7 months ago    Up 25 hours                 6379/tcp                                              socialdrop-redis
4806a1f7303d   postgres:16-alpine                          "docker-entrypoint.s…"   11 months ago   Up 25 hours (healthy)       5432/tcp                                              n8n-postgres
```

## docker network ls
```text
NETWORK ID     NAME                            DRIVER    SCOPE
e9b92e9ae770   bridge                          bridge    local
903dcc2127c8   host                            host      local
eb73051ed4f1   multica_default                 bridge    local
14d871e777a4   n8n_n8n_network                 bridge    local
e25d2408f923   none                            null      local
aa746d505ca1   services-network                bridge    local
9d2bfbaefcc2   socialdrop_socialdrop-network   bridge    local
2564df192387   supabase_default                bridge    local
bad97a522c0d   wa-bridge_default               bridge    local
```

## docker volume ls
```text
DRIVER    VOLUME NAME
local     13bed70eb8fa55c791e8b27720a03cf5f4bf571009f479572063b0df02b40618
local     21ef80214e476859f02177c6f128446864319fa42c1bc369e6f1900796f132c2
local     61b433f1a5fe8cc622799d645a8e6e4eab35196c56d98605d490ddff1daef039
local     6146d7c0d72071f326dcc752751780a3d5b06a1e388077ba64a2e39a1195f233
local     81219239b489c13a3d68d6024f6bd657755691224fb8a5d345379e4eb413e22a
local     bcf38f27f3912204d9a5aade5ee5072b1f604607974d42764b748a6728989849
local     deploy_data
local     f006de8ad3df5a2082fea10166eb4d273bb69abb724cd352f5d21483a076d5bd
local     multica_backend_uploads
local     multica_pgdata
local     multica_redis_data
local     n8n_n8n_data
local     n8n_postgres_data
local     nocodb_nc_data
local     postiz_postgres-data
local     postiz_postgres-volume
local     postiz_postiz-config
local     postiz_postiz-redis-data
local     socialdrop_postgres_data
local     socialdrop_redis_data
local     supabase_db-config
local     supabase_deno-cache
```

## df -h
```text
Filesystem      Size  Used Avail Use% Mounted on
tmpfs           1.2G  3.3M  1.2G   1% /run
/dev/sda1       193G  149G   44G  78% /
tmpfs           5.9G  1.1M  5.9G   1% /dev/shm
tmpfs           5.0M     0  5.0M   0% /run/lock
/dev/sda16      881M  117M  703M  15% /boot
/dev/sda15      105M  6.2M   99M   6% /boot/efi
tmpfs           1.2G   16K  1.2G   1% /run/user/0
overlay         193G  149G   44G  78% /var/lib/docker/rootfs/overlayfs/d26b452e1fa568e2bab86d1e5470f8f6f61ca95e2679c96182b29d05e9a60afc
overlay         193G  149G   44G  78% /var/lib/docker/rootfs/overlayfs/e620ed5a985d96617f6cc43e2fd27d086943a49e968cd13e7747b8495827881a
overlay         193G  149G   44G  78% /var/lib/docker/rootfs/overlayfs/f5f49b385d6edc4a50e47e0b4776e4cead43dddeb7f6971ee93d1383608031cc
overlay         193G  149G   44G  78% /var/lib/docker/rootfs/overlayfs/c3faa69da5a07d130917f929b9ba7c277cde75f2a0786e9c61d5cba1c6d9e194
overlay         193G  149G   44G  78% /var/lib/docker/rootfs/overlayfs/8e0d3237f1b04d770e8e47c778d81da307e46d54a79a3648243c2702a70c6f27
overlay         193G  149G   44G  78% /var/lib/docker/rootfs/overlayfs/229bd814d4ebe4fef6677e53985a6ffc7715ececb4cc8df2422fc2d84374fe48
overlay         193G  149G   44G  78% /var/lib/docker/rootfs/overlayfs/28b4a36a49d03acc6e3ed67c86c9c269232f996508c3ce2187385eda07a41518
overlay         193G  149G   44G  78% /var/lib/docker/rootfs/overlayfs/1e6a1cd8dc24f460620fddea323bf383d0039f48d9bc1f77016428cd36377806
overlay         193G  149G   44G  78% /var/lib/docker/rootfs/overlayfs/ed3b99232003358cfd4fe6dd201a139f3b53024ee048c45fb016271e1da84f54
overlay         193G  149G   44G  78% /var/lib/docker/rootfs/overlayfs/34018b20ef5bfe3ff223ab0055070b394579523d771d636587d06cbdc5dfc45e
overlay         193G  149G   44G  78% /var/lib/docker/rootfs/overlayfs/c2902090ed76f0b5fed87fe42aca48b2893c881c49c29a2faddcd230836eb1eb
overlay         193G  149G   44G  78% /var/lib/docker/rootfs/overlayfs/140d7d75c8d2e4748443adbdf9b73edbe0b66b8ee81b4036bf14d30c17090290
overlay         193G  149G   44G  78% /var/lib/docker/rootfs/overlayfs/a3051a7553d64d951df249e478d236d676aa5a69d4fbdd2126f3d7953a758018
overlay         193G  149G   44G  78% /var/lib/docker/rootfs/overlayfs/1990bd026b1cef5b25c396bb502d272e4f4203d1634c61ce7a2be6c78938367f
overlay         193G  149G   44G  78% /var/lib/docker/rootfs/overlayfs/a6517ca88c965e5506bd209d5bb11cf1fc5d07f297e831c4fced35e09208ddc6
overlay         193G  149G   44G  78% /var/lib/docker/rootfs/overlayfs/4806a1f7303db83aac0edf6e8095007f91a033cb6ef078fa5329cb33344fa3dc
overlay         193G  149G   44G  78% /var/lib/docker/rootfs/overlayfs/53ba363b68128c36ce2487adfe533ad73b1aa280ac57c97f17ec279841fa76fd
overlay         193G  149G   44G  78% /var/lib/docker/rootfs/overlayfs/d88eb116087eeb3bc557761ae95bd0f947fa02e7bf2db810ec4a058432eb62e2
overlay         193G  149G   44G  78% /var/lib/docker/rootfs/overlayfs/1a1fbc586586d5e290a5b7fc072e154154f1c45f2bacfda222bdddbeeb32b682
overlay         193G  149G   44G  78% /var/lib/docker/rootfs/overlayfs/d18319f5e6ae85201f4bd4b611f49b747f5dbf80454fa6e4cf8739e2958a6665
overlay         193G  149G   44G  78% /var/lib/docker/rootfs/overlayfs/08036505cc9e5b7a7aff9fbd76bfae9ebdfb07d90cb5587f8b5fe88e2122b181
overlay         193G  149G   44G  78% /var/lib/docker/rootfs/overlayfs/d6edf588bbe6caf59ab3376a0ee10b114f548f72dc8c43c97dc4147256af7880
overlay         193G  149G   44G  78% /var/lib/docker/rootfs/overlayfs/565d37aeb11e135f667ea738a61e5613423873dc22fa830973e58ba153e95383
overlay         193G  149G   44G  78% /var/lib/docker/rootfs/overlayfs/3a71cb5ce7e2522977245127972b1685d511401cf857dfdb78534c3de3025ce0
overlay         193G  149G   44G  78% /var/lib/docker/rootfs/overlayfs/92e3693c540ab6b7fa4307f78ceb94fb9e49c40e52e9b803e5ddb735e021e73d
overlay         193G  149G   44G  78% /var/lib/docker/rootfs/overlayfs/585a9af2acccb2ef4f8fcd2b1448dbb4ffe0752be7d883421e93fb37abd3cbe6
overlay         193G  149G   44G  78% /var/lib/docker/rootfs/overlayfs/aaa075b29387f5b3dd261b27d2e91a681305cacc14922a23307424eff91d0481
```

## root crontab -l
```text
0 3 * * * /opt/openclaw-dashboard/backup.sh >> /var/log/openclaw-backup.log 2>&1
```
