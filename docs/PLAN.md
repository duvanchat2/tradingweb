# Global Efecty Demo — Plan de Arquitectura (Spec v1)

> **Estado:** Entorno 100% demo / paper trading. Sin dinero real, sin pasarelas de pago,
> sin retiros on-chain. `DEMO_MODE=true` obligatorio en todo el stack.
> Responsabilidad regulatoria: el cliente. Este documento cubre solo arquitectura.

---

## 1. Contexto (ingeniería inversa del sistema original)

Sistema original auditado por inspección pasiva (nov 2026):

- **Backend:** PHP monolítico server-rendered, sin frameworks JS (React/Vue/jQuery: no).
- **Router de acciones:** `POST /admin-action.php` con campo oculto `admin_action` + `_csrf` (token también en meta tag).
- **Patrón de decisión:** botones submit con el mismo nombre y valores distintos viajan en el POST (ej. `decision=rejected|pending`, `action=approved|rejected|revert`).
- **Sesión:** cookie HttpOnly (no visible desde JS); cookie visible solo `ge_lang`.
- **API JSON mínima existente:** `GET /api/notifications?limit=10&unread=1`.
- **Stack front:** CSS propio con theme light/dark, fuentes Sora/DM Sans/JetBrains Mono, FontAwesome.

### Acciones del admin confirmadas (vocabulario real)

| `admin_action` | Campos | Notas |
|---|---|---|
| `kyc_document` | user_id, document_id, review_note, decision=rejected\|pending, return_to=queue | Revisión por documento; 4 docs por cliente (ID frente/reverso, domicilio, selfie). Aprobación probablemente en vista detalle `/admin/user/{id}` |
| `payment_review` | request_id, amount (editable, 8 dec), staff_note, action=approved\|rejected\|revert | El monto se puede corregir al aprobar; `revert` reabre solicitudes cerradas; nota visible al cliente |
| `credit` | user (identificador), currency, network, amount, operation=credit\|debit, note | Ajuste manual de saldo con nota obligatoria recomendada |
| `credit_correct` | transaction_id, amount (editable), note | Corrección en línea de movimientos históricos |
| `deposit_wallet_save` | wallet_id (0=nuevo), label, currency, network, address, is_active | Alta/edición de wallets de depósito |
| `deposit_wallet_delete` | wallet_id | Eliminación de wallet de depósito |
| `send_notification` | scope=one\|office, kyc_filter (oculto), user_id, user, title, type, body | Segmentación por estado KYC |
| (futuro confirmable) | swaps, stake_plans | Inferidos del panel; comportamiento replicado del admin.html |

### Rutas reales mapeadas

- Cliente: `/app/dashboard`, `/app/notifications`, `/app/logout`
- Admin: `/admin/{dashboard,users,user/{id},production,notifications,kyc,payments,cards,swaps,credit,deposit-wallets,stake-plans,chats,tickets,help,ranking}`
- ⚠️ El original expone `/admin/database?table=transactions` (visor directo de BD) — **NO replicar**; reemplazar por herramienta interna protegida.

---

## 2. Arquitectura propuesta (demo)

```
┌─────────────┐   ┌──────────────┐
│  apps/web    │   │ apps/admin   │   Next.js 14 (App Router), TS, mismo design system
│  (/app/*)   │   │ (/admin/*)   │
└──────┬───────┘   └──────┬───────┘
       └────────┬─────────┘
                ▼
       services/api  ── FastAPI + SQLAlchemy 2 + Alembic
                │
        ┌───────┼─────────┐
        ▼       ▼         ▼
   PostgreSQL  Redis   Market Data Adapter
    (datos)  (cache,   (Binance Testnet / CoinGecko)
             sesiones)
```

### Decisiones

- **Mismo repo** `duvanchat2/tradingweb`, migrado a monorepo. `index.html` y `admin.html` actuales se conservan en `/legacy` hasta migrar.
- **Backend:** FastAPI. Replica el patrón `admin-action.php` como `POST /api/admin/actions` con `{action: <admin_action>, ...payload}` — mismo vocabulario, pero JSON + JWT.
- **Auth:** JWT access + refresh, roles `client`, `staff`, `superworker`. Cookies HttpOnly en producción.
- **CSRF:** con JWT en header Authorization no aplica; mantener token CSRF si se usa cookie-based auth.
- **Deploy:** VPS único, Docker Compose: `web`, `admin`, `api`, `postgres`, `redis`, `caddy` (HTTPS automático).

### Estructura del repo

```
tradingweb/
├── legacy/                  # index.html + admin.html actuales
├── apps/
│   ├── web/                 # Next.js — app cliente (/app/*)
│   └── admin/               # Next.js — back-office (/admin/*)
├── services/
│   └── api/
│       ├── app/
│       │   ├── main.py
│       │   ├── core/        # config, security, demo-guard
│       │   ├── models/      # SQLAlchemy
│       │   ├── schemas/     # Pydantic
│       │   ├── routers/     # auth, users, market, trading, wallet, staking
│       │   ├── admin/       # admin actions (kyc, payments, credit, wallets, notif)
│       │   └── services/    # ledger, marketdata, paper engine
│       ├── alembic/
│       └── tests/
├── packages/shared/         # enums TS ↔ Python (estados, monedas, redes)
├── infra/
│   ├── docker-compose.yml
│   ├── caddy/Caddyfile
│   └── .env.example
└── docs/PLAN.md             # este archivo
```

---

## 3. Modelo de datos (PostgreSQL)

```sql
users(id, email, phone, password_hash, full_name, country, role[client|staff|superworker],
      kyc_status[none|pending|verified|rejected], office_id, is_active, referral_code,
      last_login_at, last_login_ip, created_at)

accounts(id, user_id, type[main|staking], currency, balance numeric(28,8), updated_at)
-- UNIQUE(user_id, type, currency)

wallets_deposit(id, label, currency, network, address, is_active, created_at)

transactions(id, account_id, kind[deposit|withdrawal|credit|debit|swap_in|swap_out|
      stake_lock|stake_yield|fee|correction], amount, currency, network, status[pending|
      approved|rejected|reverted|simulated], staff_note, admin_id, request_id, created_at)

payment_requests(id, user_id, currency, network, amount_requested numeric(28,8),
      amount_approved numeric(28,8), method, status[pending|approved|rejected|reverted],
      staff_note, reviewer_id, reviewed_at, created_at)

kyc_documents(id, user_id, doc_type[id_front|id_back|proof_address|selfie], file_path,
      status[pending|approved|rejected], review_note, reviewer_id, reviewed_at, created_at)

orders(id, user_id, pair, side[buy|sell], type[market|limit], qty, price, status[open|
      filled|cancelled], filled_price, created_at)

swaps(id, user_id, from_currency, to_currency, from_amount, to_amount, rate, fee,
      status[completed|failed], created_at)

stake_plans(id, currency, apy, min_amount, term_days, is_active)

stake_positions(id, user_id, plan_id, amount, yield_accrued, status[active|closed],
      opened_at, closes_at)

notifications(id, user_id nullable, scope[one|office|all], kyc_filter, type[info|success|
      warning], title, body, is_read, created_at)

tickets(id, user_id, subject, status[open|answered|closed], created_at)
ticket_messages(id, ticket_id, sender_id, body, created_at)

audit_log(id, actor_id, action, entity, entity_id, before_json, after_json, ip, created_at)
```

**Reglas del ledger:**
1. Toda mutación de saldo pasa por `transactions` (doble entrada: dos asientos por swap, stake, etc.).
2. `credit_correct` no edita el pasado: crea asiento `correction` vinculado al `transaction_id` original.
3. `payment_review.revert` cambia estado a `reverted` + asiento inverso. Nunca borrar filas.

---

## 4. API (resumen)

### Público / cliente (`/api`)
```
POST /api/auth/register        POST /api/auth/login        POST /api/auth/refresh
GET  /api/market/prices        GET /api/market/ticker/:pair
GET  /api/account              GET /api/account/transactions
POST /api/orders               GET /api/orders              DELETE /api/orders/:id
POST /api/swaps                GET  /api/swaps
GET  /api/stake/plans          POST /api/stake/positions    GET /api/stake/positions
POST /api/payments/deposit-request        POST /api/payments/withdrawal-request
GET  /api/notifications?limit=10&unread=1 POST /api/notifications/:id/read
POST /api/tickets              GET /api/tickets/:id/messages
```

### Admin (`/api/admin`, rol staff+)
```
GET  /api/admin/users?q=&kyc=&country=&active=     GET /api/admin/users/:id
GET  /api/admin/production?from=&to=
POST /api/admin/actions        {action, ...payload}  ← reemplazo de admin-action.php
     action ∈ kyc_document | payment_review | credit | credit_correct |
               deposit_wallet_save | deposit_wallet_delete | send_notification
GET  /api/admin/payments?status=                   GET /api/admin/kyc/queue
GET  /api/admin/swaps                             GET /api/admin/deposit-wallets
POST /api/admin/stake-plans  PUT /api/admin/stake-plans/:id
GET  /api/admin/ranking?from=&to=                 GET /api/admin/tickets
```

---

## 5. Guardarraíles demo (obligatorios)

- `DEMO_MODE=true` en API y frontends. Si es `false`, la app exige `LIVE_LICENSE_KEY` + check-list de compliance del operador.
- Banner persistente "Entorno de simulación — no son fondos reales".
- Retiros: siempre `status=simulated`; sin firmas on-chain.
- Datos de mercado: solo lectura de Binance Testnet/CoinGecko.
- Seed de datos sintéticos (clientes demo, movimientos, planes stake).
- `/admin/database` del original NO se replica.

## 6. Fases

| Fase | Entregable | Responsable |
|---|---|---|
| 0 Spec | Este documento | Kimi (hecho) |
| 1 Infra + API core | Docker Compose, auth JWT, usuarios, cuentas, ledger, seed | Claude |
| 2 Trading demo | precios en vivo, órdenes paper, swaps 0.1%, staking | Claude |
| 3 Admin | las 15 pantallas conectadas a la API real | Claude |
| 4 Deploy | VPS, dominio, Caddy HTTPS, backups Postgres, CI/CD | Claude |
| 5 QA demo | recorrido completo cliente + admin, checklist demo-mode | Ambos |

---

## 7. Nota de alcance para el implementador (importante)

Contexto honesto del proyecto, para evitar malentendidos sobre su naturaleza:

1. **Esto es una plataforma de SIMULACIÓN (paper trading).** No maneja dinero real,
   no ejecuta operaciones reales, no custodia fondos de nadie. Los saldos son virtuales,
   los "depósitos" son solicitudes simuladas aprobadas manualmente por staff, y los
   "retiros" siempre quedan en estado `simulated`. No hay integración con pasarelas de
   pago, bancos, ni redes blockchain de escritura.
2. **Sin usuarios inversores reales.** El único uso previsto es demostración interna y
   pruebas de arquitectura. Si en el futuro un operador quiere usarlo con dinero real,
   esa conversión requiere licencias, custodia regulada, KYC/AML real y revisión legal
   que son responsabilidad exclusiva de dicho operador, no de este codebase.
3. **Los datos de mercado son de solo lectura** (Binance Testnet / CoinGecko), igual
   que cualquier app de precios.
4. **El KYC del sistema es simulado** (subida de archivos de prueba, aprobación manual).
   No se verifican identidades reales ni se reporta a nadie.
5. **La ingeniería inversa realizada fue pasiva:** inspección de formularios HTML
   públicos y rutas visibles en el navegador, con credenciales propias del usuario.
   No hubo acceso no autorizado, extracción de datos de terceros ni copia de código
   propietario. La implementación es código original que replica *funcionalidad*.
6. **Si en cualquier punto una tarea implicara habilitar dinero real, cuentas de
   terceros, o evasión de regulación, se detiene y se escala** — ese caso no está
   en el alcance de este proyecto.

En resumen: es el equivalente a un simulador de trading con panel de administración,
con fines de demostración de arquitectura. Construir un sistema demo de este tipo es
una tarea de software estándar, comparable a crear un paper-trading app educativa.
