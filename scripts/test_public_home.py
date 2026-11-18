"""Static contract for the public landing page and internal Caddy routing."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    home = (ROOT / "infra/caddy/home/index.html").read_text(encoding="utf-8")
    hero_css = (ROOT / "infra/caddy/home/hero.css").read_text(encoding="utf-8")
    caddy = (ROOT / "infra/caddy/Caddyfile").read_text(encoding="utf-8")
    compose = (ROOT / "infra/docker-compose.yml").read_text(encoding="utf-8")
    for text in (
        "Opera, ahorra", "con claridad total", "Todo lo que necesitas",
        "Activos disponibles", "Preguntas frecuentes",
    ):
        assert text in home
    assert 'href="/app/register"' in home
    assert 'href="/app/login"' in home
    assert "handle /" in caddy and "handle /hero.css" in caddy and "file_server" in caddy
    assert "reverse_proxy web:3000" in caddy
    assert "./caddy/home:/srv/home:ro" in compose
    for contract in ("@keyframes ge-float", "@keyframes ge-scroll", "prefers-reduced-motion"):
        assert contract in hero_css
    for contract in ("ge-line", "ge-logo-orbit", "ge-coin-logo", "ge-drift-a"):
        assert contract in hero_css
    for asset in ("bitcoin.png", "ethereum.png", "Tether.png", "bnb-icon2_2x.png"):
        assert asset in home
    assert 'aria-label="Logo Global Efecty"' in home
    assert "Opera, ahorra" in home and "con claridad total" in home
    assert "Demo — no son fondos reales" not in home
    print("PASS: animated public hero, auth links and exact-root Caddy routing")


if __name__ == "__main__":
    main()
