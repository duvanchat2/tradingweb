# Panel admin: adaptación visual de la referencia

La interfaz del admin usa como referencia una auditoría visual de 15 rutas de Global Efecty, capturadas a 1440 × 900 y 390 × 844 el 22 de noviembre de 2026. El paquete de capturas se conserva fuera del repositorio porque incluye la estructura de una sesión administrativa de un tercero.

## Cambios de este PR

- Barra lateral de 272 px en escritorio, grupos de navegación, iconos SVG, estado activo y menú móvil accesible.
- Encabezado con título de la ruta, enlaces reales a ayuda y notificaciones, rol y nombre del equipo.
- Tipografía DM Sans y Sora, paleta oscura, superficies, tarjetas, formularios y tablas acordes a la referencia.
- Resumen con el código diario de la propia oficina, wallets de depósito, métricas, registros, pagos, swaps y accesos a las rutas de operación. Los valores salen de los endpoints administrativos existentes. El código solo se muestra si coincide con la oficina del usuario autenticado.
- Encabezados de sección compartidos para las demás rutas. Se conservan las operaciones, validaciones, CSRF, controles por rol y formularios existentes.

## Comportamiento y límites

Los enlaces del Resumen llevan a rutas funcionales del admin. El menú móvil abre y cierra sin modificar datos. El indicador `ES` muestra el idioma actual; la traducción completa del admin no forma parte de este cambio y no se presenta como un selector interactivo.

La auditoría de referencia no incluyó payloads ni respuestas de operaciones administrativas. Este PR no presume que el comportamiento privado de esa web sea igual al de Tradingweb. No se cambian API, esquema, permisos ni cálculos financieros.

Las wallets de depósito de Tradingweb son globales en el esquema actual. El contador del Resumen refleja ese endpoint; no se presenta como una lista exclusiva de la oficina. Un alcance por oficina requeriría una migración y revisión de permisos independientes.

## Verificación

- `npm.cmd run typecheck` en `apps/admin`.
- `npm.cmd run build` en `apps/admin`.
- Revisión local con una API simulada y datos sintéticos para las 15 rutas: cada ruta mostró encabezado y enlace activo correctos. A 390 px ninguna produjo desbordamiento horizontal; el menú móvil abrió y cerró al navegar. Se tomaron capturas de Resumen, Usuarios, Pagos y Swaps en escritorio y móvil.
- Comprobar visualmente en un entorno conectado a la API real antes de producción; la prueba local de API requiere `TEST_DATABASE_URL` y Docker no estaba disponible en el equipo de desarrollo.
