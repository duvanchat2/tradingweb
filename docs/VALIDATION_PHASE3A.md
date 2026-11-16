# Validación Fase 3a — 2026-11-15

Base final: `main` en `6942c116d176febb6625d55fca4ad2c61e480c83`, con PR #1 y #2 fusionados. La rama de esta fase se rebasó sobre esa base antes de publicar; el implementador no fusionó ningún PR.

## Backend, migraciones y stack

- **85 pruebas aprobadas**, de las cuales **38 son nuevas** para administración, PostgreSQL 16 y Redis DB 15 exclusivos para tests. Ejecutadas dentro de la imagen API compilada. Un aviso de deprecación Starlette/AnyIO de TestClient, sin fallos.
- Casos: siete acciones y permisos client→403; depósito con monto editable; aprobación/rechazo de retiro con escrow exacto; reabrir sin modificar saldos ni duplicar liquidación; crédito/débito; corrección vinculada sin editar original; wallets; filtros KYC/oficina en notificaciones; idempotencia concurrente y conflictos de clave; paginación/filtros, ámbito de oficina, perfiles y auditoría de lecturas; métricas de clientes que excluyen cuentas del equipo.
- `alembic check` sobre la BD demo: **No new upgrade operations detected**.
- Sobre una BD PostgreSQL separada: `alembic upgrade head && alembic check && alembic downgrade b42e1200f002 && alembic upgrade head && alembic check`: código de salida 0.
- Build Docker de **api y admin**: correcto. Next.js 14.2.35 completó producción, TypeScript y generación de rutas. Autoprefixer emitió un aviso no bloqueante sobre `align-items: end`.
- Se utilizó el ajuste temporal de CA BuildKit y builds secuenciales descrito en VALIDATION.md por la red y disco VFS del entorno. El certificado no se incorporó a las imágenes y TLS permaneció activo. Los Dockerfiles del repositorio no dependen de ese entorno.
- `docker compose -f infra/docker-compose.yml up -d --no-build --wait`: seis servicios levantados usando esas imágenes, API/PostgreSQL/Redis saludables. No hubo despliegue VPS.
- Consulta posterior sobre datos del smoke: **cero entry_id desbalanceados, cero saldos negativos, todas las ejecuciones de pagos simulated**. Se comprobaron eventos de auditoría admin persistidos.
- `git diff origin/main -- legacy`: vacío; HTML originales conservados.

Comando de suite verificado:

```sh
docker compose -f infra/docker-compose.yml exec -T \
  -e TEST_REDIS_URL=redis://redis:6379/15 api sh -c \
  'export TEST_DATABASE_URL="${DATABASE_URL%/*}/tradingweb_test"; pytest -q'
```

## Navegador real

`scripts/test_admin_ui.py` se ejecutó con Chromium/Playwright contra el build de producción standalone y después contra **la imagen admin Docker a través de Caddy**, en `http://admin.tradingweb.local:8080`.

Resultados del recorrido final por Caddy:

1. Visitante sin sesión llega a login; staff inicia sesión y ve Resumen.
2. Cookies de sesión HttpOnly; no hay tokens ni otros datos en localStorage.
3. Las **15 vistas** responden 200, muestran su encabezado y mantienen el banner demo: dashboard, users, production, notifications, kyc, payments, cards, swaps, credit, deposit-wallets, stake-plans, chats, tickets, help y ranking.
4. Mutación sin CSRF: **403** antes de llamar a acciones.
5. Retiro sintético de 1 USDT: aviso exacto **“Ejecución simulada — sin envío on-chain”**, aprobación mediante formulario y estado aprobado comprobado por la API.
6. Crédito manual para compensar el retiro de la prueba; reenviar el mismo formulario devuelve que ya estaba aplicado, sin segundo crédito.
7. Filtro de usuarios devuelve un registro esperado; ningún error JavaScript.
8. Eliminada la cookie access, la navegación renueva mediante refresh HttpOnly y vuelve a cargar Resumen.
9. Eliminada nuevamente access, logout renueva lo necesario, revoca la sesión y elimina las cookies de autenticación.
10. Un cliente intenta el login admin: vuelve a login con error de rol y no recibe cookies de sesión admin.

Comando por Caddy usado en esta máquina sin DNS local:

```sh
ADMIN_URL=http://admin.tradingweb.local:8080 \
ADMIN_RESOLVE_IP=127.0.0.1 \
ADMIN_REQUEST_URL=http://127.0.0.1:8080 \
ADMIN_REQUEST_HOST=admin.tradingweb.local:8080 \
python3 scripts/test_admin_ui.py
```

La resolución se limita al dominio **local de la aplicación** en Chromium. Si existe un proxy de entorno, se conserva para el resto del tráfico y se exceptúan únicamente localhost, loopback y ese dominio local. No se alteran reglas de acceso a Binance ni otros servicios externos.

También se inspeccionó visualmente Pagos a 1440px: sidebar de 272px, fondo/tarjetas/gradientes del diseño original, tipografías configuradas y radios de 20px. El aviso de retiro permanece visible tanto en pendientes como aprobados.

## Checklist PLAN.md §5

- [x] Modo demo obligatorio; `DEMO_MODE=false` continúa rechazado.
- [x] Banner persistente también en login y todas las vistas admin.
- [x] `X-Demo-Confirm: true` conservado en toda la API y enviado por el BFF.
- [x] Retiros exclusivamente simulados; sólo se liquida/devuelve saldo interno, con `execution_status=simulated` y asientos simulated.
- [x] Adaptador de mercado de sólo lectura conservado sin cambios.
- [x] Datos y pruebas exclusivamente sintéticos.
- [x] Sin `/admin/database`, consultas arbitrarias ni exposición de password_hash.
- [x] Mutaciones financieras sólo mediante ledger compensado, con transacciones y auditoría.
- [x] Sin pasarelas, firmas, transferencias on-chain ni despliegue externo.

## Límites explícitos

Chats/tickets son lectura de conversaciones existentes, sin realtime ni respuestas nuevas. Tarjetas no se emiten ni se inventan registros. Planes y swaps son tablas de lectura. Apps/web queda para integración posterior. El aviso conocido de npm sobre Next.js 14 persiste bajo el stack fijo; no se han añadido Server Actions, middleware de autorización ni optimización de imágenes.
