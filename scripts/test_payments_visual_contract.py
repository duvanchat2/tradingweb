from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_payments_workspace_matches_reference_structure():
    source = (ROOT / "apps/web/components/PaymentsWorkspace.tsx").read_text(encoding="utf-8")
    css = (ROOT / "apps/web/app/globals.css").read_text(encoding="utf-8")
    for marker in ["payment-method-picker", "payment-workspace-grid", "withdrawal-panel", "Historial de solicitudes"]:
        assert marker in source
    for marker in [".payment-workspace-grid", ".payment-method-picker", ".withdrawal-panel"]:
        assert marker in css
