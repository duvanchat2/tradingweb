from pathlib import Path

root = Path(__file__).resolve().parents[1]

schema = (root / "services/api/app/models/schema.py").read_text(encoding="utf-8")
auth = (root / "services/api/app/routers/auth.py").read_text(encoding="utf-8")
paper = (root / "services/api/app/services/paper.py").read_text(encoding="utf-8")
admin = (root / "services/api/app/admin/service.py").read_text(encoding="utf-8")
shell = (root / "apps/web/components/PanelShell.tsx").read_text(encoding="utf-8")
page = (root / "apps/web/app/(panel)/[...section]/page.tsx").read_text(encoding="utf-8")

assert "class Office(" in schema
assert all(name in schema for name in ("trading_enabled", "swap_enabled", "withdrawals_enabled", "token_secret"))
assert "current_registration_code" in auth and "office_id=office.id" in auth
assert all(value in schema for value in ("mime_type", "original_name", "file_data"))
assert "withdrawal_lock" not in paper.split("def request_withdrawal", 1)[1]
assert "source_type='main'" in admin
assert "TRADING_PAIRS" in paper and all(pair in paper for pair in (
    "BTCUSDT", "ETHUSDT", "BNBUSDT", "SOLUSDT", "XAUUSDT", "XAGUSDT"
))
assert "localStorage" in shell and "data-theme" in shell
assert "Documento parte delantera" in page
assert "Documento parte trasera" in page
assert "Prueba de residencia" in page

print("kyc/office/control UI contract: ok")
