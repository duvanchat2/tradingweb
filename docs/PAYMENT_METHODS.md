# Métodos de pago, retiros, CDT y swap

## Métodos vinculados

El cliente puede vincular tres tipos de método desde **Depositar / Retirar**:

- transferencia bancaria: alias, titular, banco, tipo de cuenta y únicamente los últimos cuatro dígitos;
- tarjeta: alias, titular, marca y únicamente los últimos cuatro dígitos;
- cripto: alias, titular, red y dirección pública de wallet.

Los métodos pertenecen al cliente autenticado, se pueden desvincular mediante baja lógica y están disponibles para el personal autorizado en **Métodos vinculados**. Cada solicitud conserva el `payment_method_id` y una descripción de destino para revisión administrativa.

La aplicación no solicita ni persiste PAN completo, fecha de vencimiento, PIN ni CVV. Los campos no permitidos se rechazan en la API. Para cobrar o abonar una tarjeta real será necesario integrar posteriormente un procesador que devuelva un token; este cambio no añade custodia ni procesamiento real.

Esta restricción sigue la [guía oficial del PCI Security Standards Council](https://www.pcisecuritystandards.org/faqs/1319/), que prohíbe conservar códigos de verificación de tarjeta después de una autorización, incluso cifrados.

## Depósitos y retiros

- Un depósito selecciona moneda, monto y un método activo del mismo cliente.
- Un retiro selecciona moneda, monto y un método activo del mismo cliente.
- La solicitud y el bloqueo contable continúan siendo simulados.
- No se publican credenciales bancarias ni datos completos de tarjetas.

## CDT

Los planes activos se limitan a USDT, 20% APY y plazo anual de 365 días. El backend vuelve a validar moneda y tasa al abrir la posición; no depende únicamente del formulario.

## Swap

Los selectores usan exclusivamente las nueve monedas ya soportadas por el backend: BTC, ETH, USDT, USDC, BNB, XRP, SOL, TRX y DOGE.
