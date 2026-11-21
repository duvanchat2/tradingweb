from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
shell = (ROOT / "apps/web/components/PanelShell.tsx").read_text(encoding="utf-8") if (ROOT / "apps/web/components/PanelShell.tsx").exists() else ""
page = (ROOT / "apps/web/app/(panel)/[...section]/page.tsx").read_text(encoding="utf-8")
css = (ROOT / "apps/web/app/globals.css").read_text(encoding="utf-8")
dockerfile = (ROOT / "apps/web/Dockerfile").read_text(encoding="utf-8")
next_config = (ROOT / "apps/web/next.config.mjs").read_text(encoding="utf-8")


assert "panel-menu-toggle" in shell
assert 'aria-controls="client-sidebar"' in shell
assert "Wallets" in shell and "Movimientos" in shell and "Depositar / Retirar" in shell
assert "panel-topbar" in shell and "panel-sidebar" in shell
assert "PRINCIPAL" in shell and "FINANZAS" in shell and "CUENTA" in shell
assert "PanelIcon" in shell
assert "async function wallets" in page
assert "async function transactions" in page
assert "async function payments" in page
assert "dashboard-status" in page and "dashboard-market-card" in page
assert "function priceRows" in page
assert "Object.entries(payload?.prices || {})" in page
assert "const prices = priceRows(marketData)" in page
assert "payload?.assets" in page
assert "clientGet('/api/market/live')" in page
assert "CryptoIcon" in page
assert "market-ticker" in page
assert "dashboard-status" in page
assert "market-filter-panel" in page
assert "transactions-panel" in page
assert 'className="dashboard-market-link" href="/market"' in page
assert "market-highlight-grid" in page
assert "portfolio-distribution" in page
assert "live-market-list" in page
assert "market-overview-hero" in page
assert "market-filter-panel" in page
assert "Ver detalles del mercado" in page
assert "Ver todas las monedas" in page
assert "Transacciones recientes" in page
assert "usePathname" in shell
assert "section===href" in shell
assert "basePath: '/app'" in next_config
assert "wallets:wallets" in page
assert "transactions:transactions" in page
assert "payments:payments" in page
assert ".panel-sidebar" in css
assert "width:272px" in css
assert "--ge-bg-primary:#0a0a0f" in css
assert "backdrop-filter:blur(24px) saturate(1.6)" in css
assert "@media(max-width:768px)" in css
assert "COPY --from=build --chown=node:node /app/public ./public" in dockerfile
assert 'src={`/app/coins/${file}`}' in (ROOT / "apps/web/components/PanelIcons.tsx").read_text(encoding="utf-8")
assert 'src="/app/brand/isotipo.svg"' in shell

print("PASS: audited dashboard shell, routes and responsive contract")
