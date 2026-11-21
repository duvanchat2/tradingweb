import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
catalog_path = ROOT / "apps/web/data/transfer-banks.json"
selector_path = ROOT / "apps/web/components/BankMethodForm.tsx"
schema_path = ROOT / "services/api/app/models/schema.py"

assert catalog_path.exists()
catalog = json.loads(catalog_path.read_text(encoding="utf-8"))
assert len(catalog) == 24
assert sum(len(rows) for rows in catalog.values()) == 263
assert catalog["Colombia"][0] == {"id": 48, "name": "Banco Agrario"}
assert any(row["name"] == "Bancolombia" for row in catalog["Colombia"])

selector = selector_path.read_text(encoding="utf-8")
assert "[country as keyof typeof transferBanks]" in selector
assert 'name="bank_country"' in selector
assert 'name="bank_id"' in selector
assert 'name="bank_name"' in selector
assert "Primero selecciona un país" in selector

schema = schema_path.read_text(encoding="utf-8")
assert "bank_country" in schema
assert "bank_id" in schema

print("PASS: static transfer-bank catalog and dependent selector contract")
