from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
model = (ROOT / "services/api/app/models/schema.py").read_text(encoding="utf-8")
client = (ROOT / "services/api/app/routers/client.py").read_text(encoding="utf-8")
trading = (ROOT / "services/api/app/services/paper.py").read_text(encoding="utf-8")
web = (ROOT / "apps/web/app/(panel)/[...section]/page.tsx").read_text(encoding="utf-8")
actions = (ROOT / "apps/web/app/backend/actions/route.ts").read_text(encoding="utf-8")
admin = (ROOT / "apps/admin/app/(panel)/[[...section]]/page.tsx").read_text(encoding="utf-8")

assert "class PaymentMethod" in model
assert "payment_method_id" in model
assert "@router.post('/payments/methods'" in client
assert "@router.get('/payments/methods'" in client
assert "@router.delete('/payments/methods/{method_id}'" in client
assert "card_last4" in client and "account_last4" in client
assert "Payment method does not belong to this user" in trading
assert "plan.currency != 'USDT'" in trading
assert "plan.apy != Decimal('20')" in trading
assert "Métodos de pago" in web
assert "Transferencia bancaria" in web and "Tarjeta" in web and "Cripto" in web
assert "name=\"payment_method_id\"" in web
assert "const currencies = ['BTC','ETH','USDT','USDC','BNB','XRP','SOL','TRX','DOGE']" in web
assert "payment_method_create" in actions and "payment_method_delete" in actions
assert "Métodos vinculados" in admin and "payment-methods" in admin

print("PASS: linked payment methods, USDT CDT and supported swap currency contract")
