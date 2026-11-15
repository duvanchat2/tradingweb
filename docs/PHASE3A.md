# Fase 3a — back-office demo

Implementado sobre `main` con Fases 1–2 fusionadas. No se modifica `legacy/`, no se habilita modo live ni se despliega fuera del stack local.

## Arranque y acceso

```sh
docker compose -f infra/docker-compose.yml up -d --build --wait
```

Abrir `http://admin.tradingweb.local:8080/admin/login`, con el archivo hosts descrito en README. Credenciales: `staff@demo.example.com` o `superworker@demo.example.com`, contraseña `SEED_PASSWORD` de `infra/.env`. Los clientes se rechazan en este login y en todos los endpoints admin.

El admin Next.js utiliza `API_INTERNAL_URL=http://api:8000`, exclusivamente del lado servidor. La API sigue recibiendo JWT por Bearer y `X-Demo-Confirm: true`; el navegador mantiene los tokens sólo en cookies **HttpOnly**, host-only, `SameSite=Strict`, path `/admin`. No se guardan tokens en localStorage ni se serializan a componentes cliente. Se renueva el access token con el refresh y se revoca la sesión al cerrar sesión, incluso si el access ya caducó. Los formularios requieren origen coincidente y un token CSRF aleatorio, enviado en cabecera o campo oculto. Las respuestas de sesión y datos no se cachean.

`ADMIN_COOKIE_SECURE=false` sirve para HTTP local. En Fase 4, al configurar HTTPS, debe ser true. No se agregan Server Actions ni middleware de autorización de Next; la autorización reside en la API y en las lecturas server-side.

## Ámbito de autorización

- `superworker`: usuarios globales y operaciones administrativas autorizadas.
- `staff`: únicamente clientes con el mismo `office_id`; si la oficina es NULL, únicamente clientes sin oficina. No puede consultar ni modificar usuarios de otras oficinas ni cuentas de staff/superworker.
- Configuración de wallets de depósito y lectura de planes son compartidas: el esquema no tiene oficina para esas entidades. Ambos roles staff+ pueden consultar configuración; las acciones de wallets están auditadas.
- Notificaciones se materializan por cliente activo. `all` significa todos los clientes permitidos al actor; `office` añade su oficina; `one` exige un `user_id` visible. El filtro KYC se aplica antes de crear las filas. No se envía correo ni mensajería externa.
- Las denegaciones por rol crean `admin.denied` en auditoría. Lecturas exitosas crean `admin.read`; mutaciones guardan actor, IP, antes/después y clave de idempotencia.

## Dispatcher JSON

`POST /api/admin/actions`, Bearer staff/superworker y confirmación demo. Cada acción se valida con Pydantic y rechaza campos desconocidos.

Hay dos significados de `action` en el vocabulario PHP original. Un objeto JSON no puede conservar ambos. El formato canónico utiliza `decision`:

```json
{"action":"payment_review","request_id":1,"decision":"approved","amount":"25.00000000","staff_note":"Revisión demo"}
```

Se acepta además el sobre `{ "action":"payment_review", "payload": { "request_id":1, "action":"approved", "staff_note":"Revisión demo" } }`. No deben enviarse claves `action` duplicadas en un mismo objeto.

| Acción | Comportamiento |
| --- | --- |
| `kyc_document` | Sólo rejected/pending; exige correspondencia usuario/documento y ámbito. Actualiza nota/revisor/fecha y estado KYC agregado: rejected si existe algún documento rechazado, pending en otro caso. Auditoría incluye estado KYC del usuario. |
| `payment_review` | Depósito pendiente aprobado: acredita amount o amount_requested desde tesorería. Retiro aprobado: liquida **exactamente** amount_requested desde escrow a tesorería. Retiro rechazado: devuelve exactamente escrow a main. Todos los asientos son simulated. |
| `credit` | Identificador de usuario por ID, correo o referido. Credit/debit compensado contra tesorería; importe positivo, nota obligatoria y red registrada en ambos asientos. |
| `credit_correct` | amount es la magnitud final deseada del asiento original de una cuenta main, incluido cero. Calcula la diferencia contra el original y correcciones previas, conserva su signo y crea asientos correction con original_transaction_id. Nunca edita el movimiento original. |
| `deposit_wallet_save` | wallet_id=0 crea; otro ID edita. Moneda validada, red, dirección, etiqueta y estado activo. |
| `deposit_wallet_delete` | Baja lógica: is_active=false. Conserva el registro y la auditoría; el endpoint de wallets activas deja de mostrarlo. |
| `send_notification` | Crea una fila por destinatario permitido, con segmento y filtro KYC. Devuelve IDs y cantidad; reintentos no replican el envío. |

### Reabrir sin mover saldos

La instrucción de esta fase reemplaza la inversión contable de PLAN.md para `revert`: **closed → pending, sin asiento ni cambio de saldo**. Se añade `payment_requests.ledger_resolution` para conservar el resultado económico: unsettled, credited, paid o released.

Reaprobar una solicitud ya liquidada no vuelve a mover fondos. Cambiar el resultado económico de un retiro ya liquidado/devuelto se rechaza con 409: requiere una nueva solicitud o un ajuste explícito y auditado. Tampoco puede cambiarse el importe ya liquidado al reabrir. Un depósito rechazado sin liquidación sí puede reabrirse y aprobarse. Los retiros no admiten importes parciales/editados al aprobar: deben consumir exactamente el bloqueo original, evitando liberar o consumir escrow de otra solicitud. La UI explica que reabrir sólo cambia revisión.

### Idempotencia

Enviar `Idempotency-Key` (máximo 128 caracteres) para cada intención. La API guarda en `audit_log` la clave por actor, hash del payload normalizado y resultado. Un bloqueo advisory de PostgreSQL y una restricción única serializan reintentos concurrentes. Misma clave/mismo payload devuelve 200 y estado actual con `replayed=true`; misma clave con payload distinto devuelve 409. El ámbito se comprueba de nuevo al reproducir el resultado.

Sin cabecera se deriva una clave permanente del payload normalizado: repetir exactamente la misma operación se deduplica. Para dos ajustes deliberadamente iguales se requieren claves distintas. Los formularios conservan la misma clave mientras no cambien los campos; “Nueva operación” inicia otra intención. Se usan bytes aleatorios compatibles también con HTTP del dominio local, sin depender de crypto.randomUUID.

Las decisiones cerradas también protegen la liquidación aunque se utilice otra clave. `credit_correct` recalcula el importe efectivo y no genera otro asiento si la magnitud ya coincide. Todas las mutaciones de saldo siguen usando `post_entry()`, con bloqueos y commit atómico junto con auditoría.

## Lecturas admin

Todas requieren `require_staff` y generan auditoría:

- `/users?q=&kyc=&country=&active=&page=&page_size=`: página desde 1, tamaño 1–100 (20 por defecto), filtros combinables.
- `/users/{id}`: perfil sin hash, cuentas, documentos y últimos 100 asientos.
- `/payments?status=`, `/kyc/queue`, `/swaps`, `/tickets`, `/notifications`: listas paginadas dentro del ámbito.
- `/production?from=&to=`: fechas ISO, UTC si no tienen zona; rechaza rangos invertidos. Clientes nuevos excluye cuentas de staff; depósitos/retiros se agregan por moneda y por liquidación, sin sumar divisas heterogéneas.
- `/deposit-wallets`, `/stake-plans`, `/ranking`, `/cards` y `/tickets/{id}/messages`: lecturas necesarias para las pantallas. Ranking ordena saldo **virtual USDT** de clientes visibles, no rentabilidad real.

## Las 15 vistas

Rutas Next bajo basePath `/admin`, con lecturas server-side y navegación propia: dashboard, users, production, payments, kyc, credit, deposit-wallets, notifications, swaps, cards, stake-plans, chats, tickets, help y ranking. `/user/{id}` añade detalle y corrección de asientos.

Se conservan los tokens del diseño original: fondo, gradientes, Sora/DM Sans/JetBrains Mono, radios de 20px y sidebar de 272px. Hay estados vacíos, filtros, paginación, confirmación de resultados, errores de carga y diseño adaptable.

Pagos ofrece cola, monto editable para depósitos pendientes, nota, aprobación/rechazo y reapertura. Los retiros muestran **“Ejecución simulada — sin envío on-chain”** y bloquean la edición del importe. KYC, fondos, wallets y notificaciones consumen acciones reales de la API. Swaps, tarjetas y planes son sólo lectura. No se inventa una tabla de tarjetas: la vista indica que el demo no emite tarjetas. Chats/tickets muestran las conversaciones existentes de tickets, sin chat realtime ni respuestas nuevas en esta subfase. Ayuda contiene instrucciones de los flujos implementados.

## Verificación

Suite con PostgreSQL y Redis exclusivos para tests:

```sh
docker compose -f infra/docker-compose.yml exec -T \
  -e TEST_REDIS_URL=redis://redis:6379/15 api sh -c \
  'export TEST_DATABASE_URL="${DATABASE_URL%/*}/tradingweb_test"; pytest -q'
docker compose -f infra/docker-compose.yml exec -T api alembic check
```

Smoke de navegador opcional: Python con Playwright y Chromium instalados, seed demo y stack iniciado. El script usa únicamente datos sintéticos, crea un retiro de 1 USDT y compensa su efecto mediante un crédito auditado; conserva el historial de pruebas.

```sh
ADMIN_URL=http://admin.tradingweb.local:8080 \
API_URL=http://127.0.0.1:8000 \
python3 scripts/test_admin_ui.py
```

Para una máquina de pruebas sin DNS/hosts configurados, `ADMIN_RESOLVE_IP=127.0.0.1` resuelve ese dominio sólo dentro de Chromium. `ADMIN_REQUEST_URL=http://127.0.0.1:8080` y `ADMIN_REQUEST_HOST=admin.tradingweb.local:8080` permiten la comprobación negativa de CSRF con el cliente HTTP de Playwright. No modifican conexiones externas ni el proveedor de mercado.

Evidencia de ejecución y checklist: [VALIDATION_PHASE3A.md](VALIDATION_PHASE3A.md).
