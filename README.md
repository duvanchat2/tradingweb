# Global Efecty — Recreación de landing page + panel admin (Wallet Cripto)

Recreación visual de [globalefecty.com](https://www.globalefecty.com/), una wallet cripto con swap, CDT/staking y transferencias internacionales. Incluye dos entregables, ambos HTML/CSS/JS autocontenidos (sin frameworks ni build step):

- **`index.html`** — landing page pública.
- **`admin.html`** — réplica del panel de administración (15 pantallas, datos 100% sintéticos).

## Vista previa

Abrir `index.html` o `admin.html` directamente en el navegador — no requiere build ni servidor.

## Análisis del sitio original

### Estructura de secciones (de arriba hacia abajo)

| # | Sección | Contenido clave |
|---|---------|------------------|
| 1 | **Header** | Logo, nav (Funciones, Activos, Staking, Seguridad, FAQ), selector de idioma, botones Iniciar sesión / Abrir wallet / Entrar |
| 2 | **Hero** | Badge "Plataforma cripto global · segura", título con texto en degradado, subtítulo, CTAs (Crear cuenta gratis / Iniciar sesión), pills de confianza (KYC, cifrado E2E, swap ágil, CDT, soporte 24/7), tarjeta flotante de wallet con balance total y 4 monedas |
| 3 | **Ticker** | Barra de precios en vivo con scroll infinito (BTC, ETH, USDT, BNB, USDC, XRP, SOL, TRX, DOGE) |
| 4 | **Stats** | 4 tarjetas: usuarios activos, volumen mensual, países, comisión de swap |
| 5 | **Funciones principales** | Grid de 6 tarjetas: Wallet multi-cripto (con 9 monedas soportadas), Swap instantáneo, CDT cripto, Seguridad bancaria, Transfer. Int., Soporte humano |
| 6 | **Mercado** | Tabla de precios en vivo: activo, precio, variación 24h, market cap, botón Comprar |
| 7 | **3 pasos** | Crea tu cuenta → Deposita o compra → Opera y gana |
| 8 | **Staking/CDT** | Tarjetas de APY anual por moneda (BTC, ETH, USDT, SOL, TRX, DOGE) con botón "Hacer stake" |
| 9 | **Seguridad** | Lista de puntos (acceso seguro, KYC, cifrado/rate-limiting) + tarjeta de auditoría de plataforma (HTTPS, Backups, Privacidad, AML/KYC) |
| 10 | **FAQ** | Acordeón con 5 preguntas frecuentes |
| 11 | **CTA final** | Caja con degradado, botones Crear cuenta gratis / Ya tengo cuenta |
| 12 | **Footer** | Marca + redes sociales, columnas de links (Producto, Plataforma, Compañía), stats resumidas, badges de confianza, línea legal |

### Lenguaje visual

- **Paleta**: fondo casi negro (`#070510`), paneles oscuros translúcidos, acentos en degradado morado→rosa (`#8b3ff0 → #c14ce0`) y cian (`#35d0e0`), verde/rojo para variaciones positivas/negativas.
- **Tipografía**: sans-serif de sistema, títulos grandes y pesados (800), texto secundario en gris-lavanda apagado.
- **Componentes recurrentes**: badges tipo "pill" con borde sutil, tarjetas con `border-radius` grande (14–22px) y bordes de 1px semitransparentes, iconos circulares/cuadrados con fondo en degradado.
- **Microinteracciones**: ticker con animación CSS de scroll continuo, acordeón FAQ con transición de altura, precios que se actualizan cada pocos segundos (simulado con JS, sin API real).

### Stack técnico de esta recreación

- HTML5 + CSS3 (variables CSS, grid/flexbox, `backdrop-filter`) — sin frameworks.
- JavaScript vanilla: genera dinámicamente el ticker, la tabla de mercado, las tarjetas de staking y el FAQ a partir de arrays de datos; incluye un `setInterval` que simula fluctuación de precios.
- Sin build step: es un único archivo `index.html` desplegable tal cual (GitHub Pages, Netlify, Vercel estático, etc.).

### Limitaciones conocidas / próximos pasos

- Los precios son datos simulados; para producción habría que conectar una API real (ej. CoinGecko) y manejar rate limits/caché.
- Los botones (Iniciar sesión, Abrir wallet, Comprar, Hacer stake) no tienen lógica de backend — son solo UI.
- Los íconos de monedas son representaciones estilizadas con emoji/texto, no los logos oficiales de cada marca.
- Falta responsive fino para pantallas muy pequeñas (<380px) en la tabla de mercado (requiere scroll horizontal).

## Análisis del panel admin (`admin.html`)

Réplica del back-office interno, levantada por inspección pasiva (screenshots + DOM, sin modificar datos reales). Todos los valores son sintéticos: `Cliente Demo 01…08`, `demo01@example.com`, código `DEM000`, wallet `0x0000demo…ab12`, IPs `10.0.0.x`.

### Tokens reales del sistema (extraídos del `:root` vivo)

- **Tipografía**: DM Sans (cuerpo) + Sora (display/títulos) + JetBrains Mono (datos).
- **Gradiente de marca original**: `#C026D3 → #7C3AED → #22D3EE`; en la réplica se usó la paleta del `index.html` (`#8b3ff0 → #c14ce0` + `#35d0e0`) sobre fondo `#070510` para mantener consistencia.
- **Métricas**: radio 20px, sidebar 272px, bordes `rgba(255,255,255,.08)`, glows 24–32px.

### Estructura

- **Header sticky (11 elementos)**: home, título de página, idioma (ES/EN/PT), toggle de tema, campana con contador y dropdown, reloj en vivo monoespaciado, botón App, badge de rol, nombre de usuario, salir.
- **Sidebar — 5 grupos**: GENERAL (Resumen) · USUARIOS (Todos los usuarios) · OPERACIONES (Producción, Notificaciones, KYC/Documentos, Pagos, Tarjetas, Swaps, Agregar fondos, Wallets depósito, Planes stake) · SOPORTE (Chat en vivo, Tickets, Centro de ayuda) · EQUIPO (Ranking oficina). Pie fijo: "Ir a la app" + "Cerrar sesión".

### Las 15 pantallas

| # | Pantalla | Contenido clave |
|---|----------|------------------|
| 1 | Resumen | Hero con chips y CTAs, código de registro diario (3 letras + 3 números), wallets de depósito, banner de pagos pendientes, 4+4 stat-cards, gráfico 7 días, últimos registros/movimientos/swaps, 7 accesos rápidos |
| 2 | Usuarios | Filtros (búsqueda, rol, KYC) y tabla ancha: ID, nombre+teléfono, email, país, rol, oficina, KYC, estado, último acceso+IP, registro |
| 3 | Producción | Rango de fechas + 4 métricas de oficina (clientes nuevos, depósitos, retiros, volumen swaps) |
| 4 | Notificaciones | Composer con pills de segmento por estado KYC, destinatario individual/grupal, título/tipo/mensaje; tabla de envíos recientes |
| 5 | KYC / Documentos | Cola de pendientes, filtros, fichas por cliente con 4 documentos (ID frente/reverso, domicilio, selfie) y acciones de estado |
| 6 | Pagos | Filas con monto editable, nota visible al cliente, Aprobar/Rechazar, y reapertura de solicitudes cerradas |
| 7 | Tarjetas | Tabla de tarjetas de clientes (vacía en el demo) |
| 8 | Swaps | Tabla desde→hacia con estado y acciones |
| 9 | Agregar fondos | Formulario crédito/débito con corrección de montos en línea |
| 10 | Wallets depósito | Alta de wallet (divisa, red, dirección, activa) + listado |
| 11 | Planes stake | Tarjetas de plan con APY, mínimo y plazo |
| 12–15 | Soporte y equipo | Chat en vivo, Tickets, Centro de ayuda (buscador + artículos), Ranking oficina (medallas + métricas) |

Navegación entre pantallas por `display:none` + JS, reloj en vivo real, dropdowns funcionales, botones de copiar y sidebar colapsable en móvil. Las tablas y formularios se renderizan desde arrays de datos sintéticos al final del archivo — cambiando esos arrays se actualiza toda la UI.

## Licencia / uso

Recreación realizada para uso propio del proyecto Global Efecty. No incluye assets ni código fuente original del sitio real — todo el HTML/CSS/JS fue escrito desde cero a partir del análisis visual de la página pública.
