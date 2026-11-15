# Fase 2 — motor de trading demo

Todas las rutas `/api/*` conservan `X-Demo-Confirm: true`. Operaciones y listas privadas requieren además `Authorization: Bearer <access_token>`. La API sigue rechazando modo live incluso con licencia.

## Arranque y migración

```sh
docker compose -f infra/docker-compose.yml up -d --build --wait
```

El arranque aplica la migración `b42e1200f002` sobre el esquema existente, sin reescribir el historial ni el seed. La migración amplía los tipos de asiento con `trade`/`withdrawal_lock`, incorpora `escrow`, estado de orden `expired`, comisión de orden y destino/ejecución de solicitudes. El downgrade es transaccional y no puede reducir el vocabulario mientras existan datos que necesiten esos tipos; no borra esos registros para forzarlo.

## Contratos

| Método y ruta | Entrada o resultado |
| --- | --- |
| `GET /api/market/prices` | Nueve activos en `prices`, valores decimales como texto, cotizados en USDT |
| `GET /api/market/ticker/{symbol}` | Precio, cambio/high/low/volume 24h, `observed_at`, `stale`, `source` |
| `POST /api/orders` | `{pair,side,qty,type?,price?}`; `type=market` por defecto |
| `GET /api/orders` | Órdenes propias, más recientes primero |
| `DELETE /api/orders/{id}` | Cancela únicamente una orden propia `open`; 404 ajena/ausente, 409 cerrada |
| `POST /api/swaps` | `{from_currency,to_currency,amount}` |
| `GET /api/swaps` | Swaps propios |
| `GET /api/stake/plans` | Planes activos |
| `POST /api/stake/positions` | `{plan_id,amount}`; transfiere de main a staking del usuario |
| `GET /api/stake/positions` | Posiciones propias; yield inicial cero |
| `POST /api/payments/withdrawal-request` | `{currency,amount,network,address}`; cola `pending`, ejecución `simulated`, fondos en escrow propio |
| `GET /api/payments/deposit-wallets` | Sólo wallets activas, lectura autenticada |

Las listas de órdenes, swaps y posiciones aceptan `limit` entre 1 y 500 (100 por defecto). Los importes requieren valor positivo, finito y máximo ocho decimales. `LedgerError` devuelve 422; ausencia de cotización utilizable devuelve 503. No se inventan precios si no existe una cotización previa.

### Mercado

`MarketDataProvider` expone `get_price(symbol)` y `get_ticker(symbol)`. La implementación se llama `BinanceTestnetProvider` según el pedido, pero consulta **sólo GET públicos de spot** en `https://api.binance.com/api/v3/ticker/price` y `/ticker/24hr`; esa URL no es testnet. No hay API key, cuenta Binance, envío de órdenes ni transferencias externas.

BTC, ETH, USDC, BNB, XRP, SOL, TRX y DOGE se consultan contra USDT; USDT es el numerario constante 1. La caché por símbolo/tipo dura cinco segundos en Redis. Tres fallos consecutivos abren el circuito compartido por proveedor durante 60 segundos. Mientras el circuito está abierto se usa el último valor conocido; si no existe, se devuelve 503. El ticker marca `stale=true` y conserva `observed_at`. El último valor conocido no expira automáticamente; la caché fresca sí. Tras el cooldown vuelve a intentarse la fuente. Timeout HTTP: tres segundos; sin redirects ni métodos de escritura.

### Órdenes y comisión

Pares paper: activo/USDT, aceptando `BTCUSDT`, `BTC/USDT` o `BTC-USDT`. Cualquier conversión entre los nueve activos se puede realizar por swaps.

- Compra: coste `qty × precio`, más comisión de 0.1% en USDT; crédito de `qty` del activo.
- Venta: débito de `qty` del activo; crédito del coste en USDT, menos comisión de 0.1% en USDT.
- Cada moneda se compensa con su cuenta de tesorería interna. Los asientos de operación son `trade`; la comisión usa `fee` y se muestra en `fee_amount`/`fee_currency`.
- Las cantidades calculadas se truncan a ocho decimales (`ROUND_DOWN`); valores calculados de cero para la operación se rechazan. Una comisión inferior a una unidad decimal mínima queda en cero y no genera asientos vacíos.
- Límites quedan `open` sin reserva. Se verifica saldo al crearlos y al ejecutarlos. El worker asyncio revisa cada cinco segundos; compra con mercado ≤ límite y venta con mercado ≥ límite, al precio observado. Si falta saldo/cotización permanecen abiertos hasta expirar a las 24 horas. La expiración no requiere consultar mercado.
- El worker usa sesiones independientes y `FOR UPDATE SKIP LOCKED` para no duplicar ejecuciones entre procesos; el loop no bloquea el event loop. Se detiene ordenadamente al cerrar la API. `LIMIT_WORKER_ENABLED` es true por defecto; false se reserva para pruebas aisladas.

### Swaps, staking y retiros

Swaps: `rate=precio_origen/precio_destino`. El importe de entrada incluye comisión: `fee=amount×0.001` en moneda origen, `to_amount=(amount-fee)×rate`. Se registran `swap_out`, `fee` y `swap_in`, todos compensados en su propia moneda. USDT↔USDC está permitido. No se aceptan monedas idénticas.

Staking: sólo planes activos, respetando mínimo y saldo. Se crea la cuenta `staking` en cero cuando hace falta; `stake_lock` mueve los fondos. La posición se registra con fecha de cierre según el plan y yield cero. No hay cálculo/acumulación automática; el job de yield corresponde a Fase 5.

Retiro: `status=pending` es exclusivamente revisión administrativa futura. `execution_status=simulated`, restringido en BD, expresa la naturaleza de la operación. `withdrawal_lock` mueve el saldo a `escrow` del mismo usuario y vincula ambos asientos con `request_id`. Network/address son datos opacos; no se firman ni envían. Aprobar/rechazar y liquidar/revertir pertenecen a Fase 3.

## Pruebas y curl reproducible

Suite completa (PostgreSQL exclusivo para pruebas y Redis DB 15):

```sh
# Crear una sola vez, si todavía no existe:
docker compose -f infra/docker-compose.yml exec -T postgres sh -c 'createdb -U "$POSTGRES_USER" tradingweb_test'
docker compose -f infra/docker-compose.yml exec -T \
  -e TEST_REDIS_URL=redis://redis:6379/15 api sh -c \
  'export TEST_DATABASE_URL="${DATABASE_URL%/*}/tradingweb_test"; pytest -q'
```

Pytest bloquea transportes HTTP reales. Provider fake y MockTransport cubren precios, TTL, circuit breaker y recuperación, compra/venta, fee exacta, swaps y stablecoins, límites/expiración/cancelación, dos workers simultáneos, gasto concurrente, aislamiento entre usuarios, staking y escrow con rollback ante saldo insuficiente.

Harness opcional de curl: **sólo en el stack de desarrollo local**. Sustituye temporalmente el proceso API por la misma aplicación con un provider fake explícito, BD `tradingweb_smoke_test`, Redis DB 14 y worker desactivado. La fábrica se niega a iniciar si esas condiciones no se cumplen; el arranque normal nunca carga este harness. Debe usarse una BD smoke nueva para reproducir exactamente los saldos de validación; no elimina ni reinicia datos existentes.

```sh
docker compose -f infra/docker-compose.yml exec -T postgres sh -c 'createdb -U "$POSTGRES_USER" tradingweb_smoke_test'
docker compose -f infra/docker-compose.yml -f infra/docker-compose.smoke.yml up -d --no-build --wait api
python3 scripts/smoke_phase2.py
# Restaurar el provider normal y activar nuevamente el worker:
docker compose -f infra/docker-compose.yml up -d --no-build --wait api
```

El script usa curl para **cada endpoint nuevo**, envía confirmación demo y Bearer, comprueba comisiones y estados, y no imprime contraseñas ni tokens. La contraseña se lee del `.env` local generado en Fase 1. No es una verificación de disponibilidad de Binance: esa consulta se comprueba por separado y puede estar restringida regionalmente.
