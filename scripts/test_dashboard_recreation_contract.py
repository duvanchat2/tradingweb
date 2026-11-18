from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
shell = (ROOT / "apps/web/components/PanelShell.tsx").read_text(encoding="utf-8") if (ROOT / "apps/web/components/PanelShell.tsx").exists() else ""
page = (ROOT / "apps/web/app/(panel)/[...section]/page.tsx").read_text(encoding="utf-8")
css = (ROOT / "apps/web/app/globals.css").read_text(encoding="utf-8")


assert "panel-menu-toggle" in shell
assert 'aria-controls="client-sidebar"' in shell
assert "Wallets" in shell and "Movimientos" in shell and "Depositar / Retirar" in shell
assert "panel-topbar" in shell and "panel-sidebar" in shell
assert "async function wallets" in page
assert "async function transactions" in page
assert "async function payments" in page
assert "quick-actions" in page and "portfolio-hero" in page
assert "function priceRows" in page
assert "Object.entries(payload?.prices || {})" in page
assert "const prices = priceRows(marketData)" in page
assert "wallets:wallets" in page
assert "transactions:transactions" in page
assert "payments:payments" in page
assert ".panel-sidebar" in css
assert "width:272px" in css
assert "@media(max-width:850px)" in css

print("PASS: audited dashboard shell, routes and responsive contract")
