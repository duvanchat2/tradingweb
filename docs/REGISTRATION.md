# Registro de clientes y texto demo

- Ruta pública: `/app/register`, enlazada desde `/app/login`; enlace de vuelta a login en el registro.
- El código de registro tiene 3 letras y 3 números, se genera por oficina activa y fecha de Colombia, y se renueva a medianoche. El administrador lo copia desde su dashboard; el superadministrador puede ver los códigos de todas las oficinas activas.
- Formulario: nombre completo, correo, contraseña de 12–128 caracteres y confirmación. Se mantiene el diseño oscuro del portal; el HTML adjunto del usuario se usa como referencia visual, no como instrucciones ejecutables.
- El BFF `POST /app/session/register` verifica origen y CSRF antes de llamar a `/api/auth/register` con `X-Demo-Confirm: true`. Sólo envía nombre, correo y contraseña; no acepta roles del formulario.
- Tras crear la cuenta redirige a login con confirmación. Maneja correo duplicado, datos inválidos, contraseñas distintas y falta de disponibilidad. Ninguna contraseña aparece en la URL ni en logs de la prueba.
- Las cuentas se crean como client con nueve cuentas principales en cero. No se asignan fondos ni se cambia la API de autenticación.
- Por la última instrucción del usuario, se retiran los banners, etiquetas y textos informativos de demo/simulación de app y admin, sin texto sustituto. Se mantienen errores de validación y confirmaciones funcionales. No cambia `DEMO_MODE`, el ledger, permisos, CSRF ni la confirmación obligatoria de la API; `/api/meta` permanece intacto.

## Verificación local

- `python scripts/test_client_ui_contract.py`: PASS.
- `npm run build` en apps/web y apps/admin: compilación de producción y TypeScript correctos. El admin mantiene el aviso no bloqueante de Autoprefixer ya existente.
- `python scripts/test_registration_ui.py`, con API demo local y web en `127.0.0.1:3050`: PASS en Chromium real. Cubre enlace desde login, ausencia de avisos demo, rechazo sin CSRF, validación y recuperación de contraseñas distintas, alta real, duplicado, validación server-side, login, cookies HttpOnly, perfil, ausencia de tokens en localStorage y nueve saldos cero.
- Se crea un único cliente sintético por ejecución del smoke, sin fondos reales. La prueba se limita a URLs loopback. Playwright y Chromium son dependencias de verificación opcionales, no del despliegue.

No se despliega ni se modifica el VPS desde este cambio.
