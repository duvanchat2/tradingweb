# Validación Fase 2 — 2026-11-15

## Resultados

- **47 pruebas aprobadas** (14 existentes + 33 nuevas), PostgreSQL 16 real y Redis DB 15 exclusivo. Suite ejecutada también desde la imagen API compilada. Un aviso de deprecación de Starlette/AnyIO en TestClient; cero fallos. Los transportes HTTP reales están bloqueados en pytest.
- Build Docker de la API actualizado: correcto. Por la CA del proxy y el disco VFS del entorno se reutilizó el mecanismo temporal descrito en VALIDATION.md: secreto BuildKit para confianza TLS y Dockerfile temporal fuera del repositorio. No se desactivó TLS ni se añadieron certificados a la imagen.
- `alembic upgrade head` sobre la BD demo existente: correcto; `alembic check`: **No new upgrade operations detected**.
- En una BD nueva `tradingweb_migrations_test`: `alembic upgrade head && alembic check && alembic downgrade 7543f0225248 && alembic upgrade head`: código de salida 0. El harness smoke también inició desde una BD nueva y aplicó ambas migraciones.
- API normal restaurada después del harness; worker habilitado por defecto, sin provider fake en el arranque habitual.

## Curl de todos los endpoints nuevos

Ejecutado `python3 scripts/smoke_phase2.py` contra la misma API mediante el harness de integración con cotizaciones fake explícitas, base `tradingweb_smoke_test`, Redis DB 14 y worker desactivado. Todas las llamadas enviaron `X-Demo-Confirm: true`; las privadas incluyeron JWT real obtenido por login. No se imprimieron tokens ni contraseñas.

| Llamada | Resultado |
| --- | --- |
| `GET /api/market/prices` | 200, nueve activos |
| `GET /api/market/ticker/BTC` | 200, `source=integration-fixture` |
| `POST /api/orders` market | 201, filled, compra 2 BTC a 100 USDT, fee 0.2 USDT |
| `POST /api/orders` limit | 201, open |
| `GET /api/orders` | 200, órdenes propias |
| `DELETE /api/orders/{id}` | 200, cancelled |
| `POST /api/swaps` | 201, 1 BTC → 9.99 ETH, fee 0.001 BTC |
| `GET /api/swaps` | 200 |
| `GET /api/stake/plans` | 200 |
| `POST /api/stake/positions` | 201, bloqueo 100 USDT, yield cero |
| `GET /api/stake/positions` | 200 |
| `POST /api/payments/withdrawal-request` | 201, pending y ejecución simulated |
| `GET /api/payments/deposit-wallets` | 200, lista de wallets activas (vacía en este seed) |

Verificación posterior de esa BD: **todos los entry_id compensados**, **ningún saldo negativo**, **25 USDT en escrow del usuario**, **yield cero** y retiro con ejecución exclusivamente simulada. Login y logout del harness: 200 y 204.

## Fuente externa real

Consulta pública directa a `https://api.binance.com/api/v3/ticker/price?symbol=BTCUSDT`: **HTTP 451**, con respuesta del proveedor indicando restricción regional. No se intentó evadirla ni se cambió a otra región/host. La API normal, con confianza TLS configurada mediante un montaje temporal de la CA del entorno, devuelve **503** en `/api/market/ticker/BTC` al no existir cotización previa. El fallback/circuit breaker y las respuestas válidas se verificaron determinísticamente con MockTransport y Redis real; **el harness no demuestra disponibilidad del proveedor externo desde esta máquina**.

## Checklist PLAN.md §5

- [x] `DEMO_MODE=true` obligatorio en API y frontends; modo live continúa rechazado.
- [x] Banner persistente existente conservado en ambos frontends; `/api/meta` y confirmación demo conservados.
- [x] Retiros sin ejecución real: revisión `status=pending` conforme al pedido, `execution_status=simulated` con CHECK SQL y asientos `simulated`; fondos sólo en escrow interno. Liquidación/reversión administrativa pendiente de Fase 3.
- [x] Mercado exclusivamente de lectura: GET públicos sin API key y sin envío de órdenes externas.
- [x] Seed y harness exclusivamente sintéticos; no se usan datos de inversores ni identidades reales.
- [x] `/admin/database` no implementado.
- [x] Toda variación de saldo pasa por `post_entry()`; pruebas de doble gasto, fee, rollback, aislamiento y workers concurrentes aprobadas.
- [x] Sin despliegue VPS ni fusión de PR por el implementador.
