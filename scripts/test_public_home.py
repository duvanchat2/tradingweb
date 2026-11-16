"""Static contract for the public landing page and internal Caddy routing."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    home = (ROOT / "infra/caddy/home/index.html").read_text(encoding="utf-8")
    caddy = (ROOT / "infra/caddy/Caddyfile").read_text(encoding="utf-8")
    compose = (ROOT / "infra/docker-compose.yml").read_text(encoding="utf-8")
    for text in (
        "Opera, ahorra", "Todo lo que necesitas", "Activos disponibles",
        "Seguridad por diseño", "Preguntas frecuentes", "Demo — no son fondos reales",
    ):
        assert text in home
    assert 'href="/app/register"' in home
    assert 'href="/app/login"' in home
    assert "handle /" in caddy and "file_server" in caddy
    assert "reverse_proxy web:3000" in caddy
    assert "./caddy/home:/srv/home:ro" in compose
    print("PASS: public home content, auth links and exact-root Caddy routing")


if __name__ == "__main__":
    main()
