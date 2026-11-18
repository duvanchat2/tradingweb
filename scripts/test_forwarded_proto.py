from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CADDY = (ROOT / "infra/caddy/Caddyfile").read_text(encoding="utf-8")


def test_public_scheme_is_preserved_for_next_apps():
    directive = "header_up X-Forwarded-Proto {http.request.header.X-Forwarded-Proto}"
    assert CADDY.count(directive) >= 2, (
        "web and admin proxies must preserve Nginx's public HTTPS scheme"
    )


if __name__ == "__main__":
    test_public_scheme_is_preserved_for_next_apps()
    print("PASS: Caddy preserves the public scheme for web and admin")
