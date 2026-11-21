import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
package = json.loads((ROOT / "apps/web/package.json").read_text(encoding="utf-8"))
icons = (ROOT / "apps/web/components/PanelIcons.tsx").read_text(encoding="utf-8")
market = (ROOT / "apps/web/components/MarketExplorer.tsx").read_text(encoding="utf-8")
css = (ROOT / "apps/web/app/globals.css").read_text(encoding="utf-8")

assert "lucide-react" in package["dependencies"]
assert "motion" in package["dependencies"]
assert "@playwright/test" in package["devDependencies"]
assert "@axe-core/playwright" in package["devDependencies"]
assert "@fontsource-variable/manrope" in package["dependencies"]
assert "@fontsource-variable/sora" in package["dependencies"]
assert "from 'lucide-react'" in icons
assert 'aria-live="polite"' in market
assert 'type="button"' in market
assert "prefers-reduced-motion:reduce" in css
assert "font-variant-numeric:tabular-nums" in css

print("PASS: Lucide, Motion-ready UI, Playwright/axe and accessible market controls")
