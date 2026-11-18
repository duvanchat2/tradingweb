from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
HTML = (ROOT / "infra/caddy/home/index.html").read_text(encoding="utf-8")
CADDY = (ROOT / "infra/caddy/Caddyfile").read_text(encoding="utf-8")


def require(*needles: str) -> None:
    missing = [needle for needle in needles if needle not in HTML]
    assert not missing, f"missing landing contracts: {missing}"


def test_reference_sections_are_complete() -> None:
    require(
        "48,329+",
        "$125M+",
        "Todo lo que necesitas",
        "Wallet multi-cripto",
        "Swap instantáneo",
        "Precios claros para",
        "data-market-row=\"BTC\"",
        "Tu primera operación",
        "Pon tus criptos a",
        "Tu dinero,",
        "Auditoría de plataforma",
    )


def test_all_nine_assets_have_real_logos() -> None:
    for symbol in ("BTC", "ETH", "USDT", "BNB", "USDC", "XRP", "SOL", "TRX", "DOGE"):
        require(f'data-asset="{symbol}"', f'alt="{symbol}"')


def test_live_market_is_same_origin_and_assets_are_served() -> None:
    require('src="/market.js"')
    assert "handle /market-data" in CADDY
    assert "@homeAssets path /hero.css /sections.css /market.js" in CADDY


def test_bottom_cta_and_full_footer_match_reference() -> None:
    require(
        "Empieza a operar",
        "Únete a más de 48,000 usuarios",
        "PRODUCTO",
        "PLATAFORMA",
        "COMPAÑÍA",
        "Custodia y seguridad",
        "Precios en vivo",
        "AML / KYC",
        "Operación global",
        "support@globalefecty.com",
        "Las criptomonedas son activos volátiles",
    )
    for network in ("X", "Telegram", "Discord", "GitHub"):
        require(f'aria-label="{network}"')


if __name__ == "__main__":
    test_reference_sections_are_complete()
    test_all_nine_assets_have_real_logos()
    test_live_market_is_same_origin_and_assets_are_served()
    test_bottom_cta_and_full_footer_match_reference()
    print("public landing sections contract: ok")
