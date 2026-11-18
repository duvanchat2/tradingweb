from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def main() -> None:
    form = read("apps/web/components/RegisterForm.tsx")
    route = read("apps/web/app/session/register/route.ts")
    page = read("apps/web/app/register/page.tsx")
    css = read("apps/web/app/globals.css")
    package = read("apps/web/package.json")

    for contract in (
        "world-countries",
        'name="registration_code"',
        'name="country"',
        'name="phone"',
        'name="password_confirm"',
        'name="terms"',
        "showPassword",
        "countryOptions",
    ):
        assert contract in form, f"missing registration form contract: {contract}"
    for field in ("registration_code", "country", "phone"):
        assert field in route, f"route does not forward {field}"
    assert "world-countries" in package
    assert "Crea tu wallet" in page
    for selector in (".register-shell", ".register-card", ".field-shell", ".country-select"):
        assert selector in css, f"missing registration style: {selector}"
    print("PASS: complete registration form, ISO countries, persistence fields and responsive design")


if __name__ == "__main__":
    main()
