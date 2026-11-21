# Datos de mercado y gráficos

## Decisión

- Los cuatro mercados cripto (`BTCUSDT`, `ETHUSDT`, `BNBUSDT`, `SOLUSDT`) conservan Binance Spot público como fuente de precio, ticker y velas. No se usan credenciales de trading.
- CoinGecko queda para la portada y metadatos de cripto. No es la fuente adecuada para `XAU` y `XAG` spot.
- TradingView puede incorporarse como gráfico visual alojado, con su atribución. No debe alimentar el ledger ni decidir el precio de una orden: sus widgets no son una API general de datos para el backend.
- `XAUUSDT` y `XAGUSDT` están en la lista funcional, pero su ejecución debe permanecer bloqueada hasta configurar un proveedor de metales con precio y velas auditables. El candidato recomendado es Twelve Data (`XAU/USD` y `XAG/USD`) y una conversión documentada USD/USDT. No se sustituirán por símbolos aproximados.

## Regla de seguridad

La interfaz puede mostrar un gráfico de TradingView, pero cada orden simulada obtiene el precio desde el proveedor del backend. Si no hay cotización vigente, la API responde como no disponible y no muta saldos.

## Pendiente de configuración

Antes de habilitar XAU/XAG en producción: contratar/configurar la fuente, añadir su clave sólo al `.env` del VPS, cachear última cotización con marca de obsolescencia y cubrir precio, ticker y velas con pruebas de transporte simulado.
