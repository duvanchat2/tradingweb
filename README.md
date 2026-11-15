# Tradingweb — demo / paper trading

Plataforma de simulación: **sin dinero real**, pasarelas, custodia ni operaciones on-chain. `DEMO_MODE=true` obligatorio. Fase 1 implementa infraestructura y API core; las interfaces sólo muestran el estado de la fase y el banner demo.

## Levantar en local

Requisitos: Docker Engine con Compose v2 y Python 3 para generar los secretos locales.

```sh
python3 infra/init_env.py
cd infra
docker compose up -d --build --wait
```

Tras la preparación inicial de `.env`, `docker compose up` inicia los seis servicios, aplica Alembic y ejecuta el seed automáticamente. No se requiere PostgreSQL, Redis, Python ni Node instalados en el host para ejecutar el stack. El generador no sobrescribe un `.env` existente. Las claves nunca se incorporan a imágenes ni commits.

- API: http://127.0.0.1:8000/docs; estado: http://127.0.0.1:8000/healthz.
- Caddy: puerto local 8080. Añadir `127.0.0.1 tradingweb.local api.tradingweb.local admin.tradingweb.local` al archivo hosts del equipo para navegar a `http://tradingweb.local:8080/app` y `http://admin.tradingweb.local:8080/admin`.
- Sin cambiar DNS: `curl -H 'Host: api.tradingweb.local' -H 'X-Demo-Confirm: true' http://127.0.0.1:8080/api/meta`.
- PostgreSQL 16 y Redis 7 no se exponen al host. Datos persistidos en volúmenes nombrados.
- Detener: `docker compose down` desde `infra/`; conserva los datos.

Todos los endpoints `/api/*`, incluidos registro/login/meta, requieren `X-Demo-Confirm: true` (sin ella: 428). Auth utiliza `Authorization: Bearer <access_token>`; no usa cookies ni almacena tokens en los frontends.

## Credenciales del seed (sólo desarrollo)

| Rol | Correos | Contraseña |
| --- | --- | --- |
| client | `client1@demo.example.com` … `client8@demo.example.com` | valor de `SEED_PASSWORD` en `infra/.env` |
| staff | `staff@demo.example.com` | valor de `SEED_PASSWORD` en `infra/.env` |
| superworker | `superworker@demo.example.com` | valor de `SEED_PASSWORD` en `infra/.env` |

Los diez usuarios comparten esa contraseña **generada localmente**, que no se documenta como literal para evitar credenciales hardcodeadas. Se almacena con Argon2 en la BD. Cambiar la variable después del seed no modifica las contraseñas ya almacenadas. El seed es idempotente y usa un bloqueo advisory PostgreSQL para serializar ejecuciones concurrentes.

Datos: 8 clientes, staff, superworker; BTC/ETH/USDT/USDC/BNB/XRP/SOL/TRX/DOGE con 1000 unidades virtuales iniciales por usuario; 20 transferencias adicionales; tres depósitos simulados (uno pendiente); cuatro KYC pendientes; un plan de staking sintético.

## Auth y API core

- `POST /api/auth/register`: `{email, password, full_name}`; siempre crea `client` y nueve cuentas en cero. Contraseña: 12–128 caracteres.
- `POST /api/auth/login`: `{email, password}`; JWT access de 15 minutos y refresh de 7 días por defecto; límite de 20 intentos/minuto por IP.
- `POST /api/auth/refresh`: `{refresh_token}`; rotación de un solo uso, revocación por replay.
- `POST /api/auth/logout`: Bearer access; revoca esa sesión en Redis.
- `GET /api/auth/me`: usuario activo autenticado, sin hash de contraseña.
- `GET /api/meta`: `{demo_mode: true, message: "Entorno de simulación"}`.
- `GET /healthz`: comprueba PostgreSQL y Redis.

Ledger `app/services/ledger.py`: `post_entry()` es la única vía de mutación del saldo. Dos asientos con moneda idéntica, suma cero, precisión decimal de ocho lugares, bloqueo de filas por ID, restricción SQL de saldo no negativo y auditoría. No se modifica ni borra el historial. La operación recibe una sesión SQLAlchemy y el llamador realiza commit/rollback.

## Verificar

Desde la raíz, con el stack levantado:

```sh
sh scripts/smoke.sh
# PostgreSQL exclusivo para tests (crear una vez):
docker compose -f infra/docker-compose.yml exec -T postgres sh -c 'createdb -U "$POSTGRES_USER" tradingweb_test'
docker compose -f infra/docker-compose.yml run --rm --entrypoint sh \
  -e TEST_REDIS_URL=redis://redis:6379/15 api \
  -c 'export TEST_DATABASE_URL="${DATABASE_URL%/*}/tradingweb_test"; pytest -q'
# Migración/modelos sin divergencias:
docker compose -f infra/docker-compose.yml exec -T api alembic check
# Seed repetible:
docker compose -f infra/docker-compose.yml exec -T api python -m app.seed
```

Las pruebas usan PostgreSQL real, una base dedicada terminada en `_test` y Redis DB 15. Eliminan únicamente las tablas de esa base y limpian ese namespace Redis. Cubren auth, replay, logout, usuario inactivo, demo obligatorio, precisión, compensación de asientos, rollback, monedas distintas, saldos negativos y dos débitos concurrentes contra la misma cuenta. El smoke script usa **curl**, sin imprimir tokens ni contraseñas.

Migraciones: `alembic upgrade head` y `alembic downgrade base` dentro del contenedor API; el downgrade destruye el esquema y sólo debe usarse sobre datos desechables. El archivo inicial contiene operaciones de esquema explícitas de las 14 entidades de PLAN.md §3.

## Estructura

```text
legacy/              HTML originales conservados byte a byte
apps/web/            Next.js 14 + TypeScript, /app
apps/admin/          Next.js 14 + TypeScript, /admin
services/api/        FastAPI, SQLAlchemy 2, Alembic, tests, fixtures
packages/shared/     ubicación para contratos compartidos
infra/               Compose, Caddyfile, .env.example, generador de secretos
docs/                PLAN.md, DEVIATIONS.md y reporte de validación
scripts/             smoke de autenticación con curl
```

Variables documentadas en `infra/.env.example`. Para ejecutar la API fuera de Compose: Python 3.12, instalar `services/api/requirements.txt`, configurar `DATABASE_URL`, `REDIS_URL`, `JWT_SECRET` y `SEED_PASSWORD`, y ejecutar desde `services/api`: `alembic upgrade head`, `python -m app.seed`, `uvicorn app.main:app`. Compose fija JWT HS256 y modo demo; TTLs, dominio y puertos se pueden configurar en `.env`.

## Estado por fases

- [x] Fase 0: especificación conservada en `docs/PLAN.md`.
- [x] Fase 1: monorepo, Compose, API core, ledger, auth, migración, seed y pruebas.
- [ ] Fase 2: mercado de sólo lectura, órdenes paper, swaps, staking.
- [ ] Fase 3: pantallas admin e integración cliente/API.
- [ ] Fase 4: VPS, dominio, HTTPS público, backups y CI/CD.
- [ ] Fase 5: QA del recorrido completo cliente/admin.

## Guardarraíles de PLAN.md §5

- [x] Modo demo por defecto y rechazo de `false`, incluso con licencia.
- [x] Banner persistente en ambos frontends y metadatos demo en API.
- [x] Confirmación explícita `X-Demo-Confirm: true` en todo `/api/*`.
- [x] Seed exclusivamente sintético; no hay identidades reales.
- [x] Sin envío on-chain ni pasarelas. Las transacciones del ledger son `simulated`.
- [x] `/admin/database` y APIs de acceso directo a tablas no implementadas.
- [ ] Ruta de retiro siempre `simulated`: pendiente de Fase 2; no existe ruta de retiro en Fase 1.
- [ ] Adaptador de mercado sólo lectura: pendiente de Fase 2; no existe integración en Fase 1.

Decisiones de alcance y extensiones mínimas del esquema: [docs/DEVIATIONS.md](docs/DEVIATIONS.md). Evidencia de ejecución: [docs/VALIDATION.md](docs/VALIDATION.md).
