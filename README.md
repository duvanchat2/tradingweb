# Global Efecty — Recreación de landing page (Wallet Cripto)

Recreación visual del landing page de [globalefecty.com](https://www.globalefecty.com/), una wallet cripto con swap, CDT/staking y transferencias internacionales. El sitio fue reconstruido desde cero como HTML/CSS/JS autocontenido (sin frameworks ni dependencias externas), replicando estructura, copy y componentes de UI de la página original.

## Vista previa

Abrir `index.html` directamente en el navegador — no requiere build ni servidor.

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

## Licencia / uso

Recreación realizada para uso propio del proyecto Global Efecty. No incluye assets ni código fuente original del sitio real — todo el HTML/CSS/JS fue escrito desde cero a partir del análisis visual de la página pública.
