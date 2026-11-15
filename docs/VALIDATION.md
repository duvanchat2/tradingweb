# Validación de Fase 1

Fecha: 2026-11-15. Entorno local gestionado, Python 3.12.14, Docker Engine 29.9.2 y Compose 2.40.3. No hubo despliegue VPS.

## API y datos

- `docker compose -f infra/docker-compose.yml up -d --no-build --wait api`: API, PostgreSQL 16 y Redis 7 saludables; arranque aplica migración inicial y seed.
- `pytest -q` dentro del contenedor API con PostgreSQL dedicado `tradingweb_test` y Redis DB 15: **14 passed**. Un aviso de deprecación de Starlette/AnyIO en el cliente de pruebas; no hubo fallos.
- `sh scripts/smoke.sh`: **PASS**, con curl real: register 201, login, me y refresh correctos, logout 204, access revocado 401 y falta de confirmación demo 428. El script no imprime secretos.
- Login adicional con curl para `client1@demo.example.com` y el `SEED_PASSWORD` generado: **PASS**.
- `alembic check`: **No new upgrade operations detected** sobre PostgreSQL del stack.
- En PostgreSQL exclusivo para pruebas: `alembic upgrade head && alembic check && alembic downgrade base && alembic upgrade head`: código de salida 0.
- `python -m app.seed` repetido: **Demo seed already present**; no duplica datos.
- Consulta de integridad del seed: **14 tablas de dominio**, **10 usuarios demo**, **3 solicitudes de depósito** (1 pendiente), **4 KYC pendientes**, **0 saldos negativos**, **0 entry_id desbalanceados**. El smoke crea además un usuario sintético de registro sin saldo.
- Los tests verifican saldo negativo, precisión, rollback, monedas incompatibles, suma cero por entrada y gasto concurrente: de dos transferencias de 7 contra saldo 10, sólo una puede confirmarse.
- Las pruebas de configuración verifican rechazo de `DEMO_MODE=false` tanto sin licencia como con una licencia presente.

## Compilación y entorno

El build ordinario se intentó primero. La red del entorno requiere una CA de proxy adicional y el almacenamiento Docker usa VFS con un límite de disco reducido. Para ejecutar la validación se utilizaron Dockerfiles temporales **fuera del repositorio**, con la CA montada como secreto BuildKit sólo en la instalación de paquetes y los pasos de instalación/compilación agrupados. Los builds se ejecutaron secuencialmente y se limpió únicamente la caché generada durante esta sesión. No se desactivó TLS ni se incorporó la CA a las imágenes finales. El Compose y los Dockerfiles entregados son independientes de este entorno.

Las imágenes se construyen con los mismos fuentes, lockfiles, versiones y comandos de build del repositorio; el ajuste es exclusivamente de confianza TLS y almacenamiento de la máquina de pruebas.

## Stack completo y frontends

- `docker compose -f infra/docker-compose.yml up -d --no-build --wait`: los seis servicios iniciados correctamente usando las imágenes compiladas en esta sesión.
- `npm ci && npm run build` en los builds Docker de **web y admin**: compilación de producción, comprobación de TypeScript y prerenderizado completados con Next.js 14.2.35.
- Curl a través de Caddy: `Host: api.tradingweb.local` + `/api/meta`, `Host: tradingweb.local` + `/app`, y `Host: admin.tradingweb.local` + `/admin`: **HTTP 200** en los tres casos. Los dos HTML incluyen el banner «no son fondos reales».
- Se establece `NO_PROXY` para los nombres internos de Compose, evitando que un proxy heredado del host intercepte el reverse proxy entre contenedores.
- Ambos archivos en `legacy/` comparados contra `main` mediante lectura binaria de Git: **idénticos byte a byte**.

## Auditoría de dependencias

`npm audit --package-lock-only` se ejecutó sobre el frontend. PostCSS se actualizó a **8.5.33** mediante override en ambas apps: sus avisos quedaron resueltos. Auditoría residual: **1 dependencia con severidad crítica (Next.js 14.2.35)**; npm propone Next.js 16.4.6, fuera del stack fijo solicitado. Incluye avisos del optimizador de imágenes, Windows y otras funciones del framework. Las imágenes ejecutan Linux; el optimizador está desactivado y estas interfaces no usan Server Actions ni middleware de autorización. Esto reduce exposición pero **no equivale a una auditoría limpia**. Revisar la rama Next.js antes de Fase 4. El stack sólo publica servicios en loopback.

## Guardarraíles

- Modo demo obligatorio y metadatos de simulación.
- Banner persistente verificado en ambos frontends a través de Caddy.
- Cabecera `X-Demo-Confirm: true` en todas las rutas `/api/*`.
- Datos y KYC sintéticos; ledger sin fondos reales, llamadas de pago ni firmas on-chain.
- No existe `/admin/database`.
- Retiros y adaptador de mercado aún no implementados: no hay salida de fondos ni integración externa en Fase 1.
