"""Static contract for the Phase 3B customer application.

This deliberately runs without Node, a browser, or a live API so CI can catch
accidental removal of the customer routes and the cookie/CSRF guardrails.
"""
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def read(path: str) -> str:
    target = ROOT / path
    assert target.exists(), f"missing {path}"
    return target.read_text(encoding="utf-8")


def main() -> None:
    session = read("apps/web/lib/session.ts")
    compact = session.replace(" ", "")
    assert "httpOnly:true" in compact
    assert "sameSite:'strict'" in compact
    assert "WEB_COOKIE_SECURE" in session
    assert "timingSafeEqual" in session

    login = read("apps/web/app/session/login/route.ts")
    assert "validCsrf" in login
    assert "role!=='client'" in login.replace(" ", "")

    actions = read("apps/web/app/backend/actions/route.ts")
    for action in (
        "order",
        "cancel_order",
        "swap",
        "stake",
        "withdrawal",
        "deposit_request",
        "notification_read",
        "ticket",
    ):
        assert f"'{action}'" in actions

    page = read("apps/web/app/(panel)/[...section]/page.tsx")
    for route in (
        "dashboard",
        "market",
        "orders",
        "swap",
        "stake",
        "wallet",
        "notifications",
        "support",
        "profile",
    ):
        assert f"{route}:" in page
    assert "demo-pill" not in page and "simulation-note" not in page
    for app in ("web", "admin"):
        layout = read(f"apps/{app}/app/layout.tsx")
        assert "demo-banner" not in layout
        assert "DEMO_MODE" in layout

    css = read("apps/web/app/globals.css")
    assert "@media" in css and ".sidebar" in css
    print("PASS: customer UI routes, actions, responsive shell, cookie and CSRF guardrails")


if __name__ == "__main__":
    main()
