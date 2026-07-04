"""Rebuild the local ledger from Cognee's raw stored documents.

Run this after a fresh clone when connecting to an existing Cognee dataset —
the ledger (backend/ledger.jsonl) is local state, and without it the
Consistency Scorer sees zero actions. Safe to re-run: it rebuilds from
scratch, never duplicates.
"""
from app import cognee_client, config, ledger

# rebuild, don't append — running twice must not duplicate
ledger._LEDGER.unlink(missing_ok=True)

datasets = cognee_client.list_datasets()
ds = next((d for d in datasets if d["name"] == config.DATASET_NAME), None)
if ds is None:
    print(f"dataset '{config.DATASET_NAME}' not found — run seed_demo.py first, "
          "or check COGNEE_* keys in .env")
    raise SystemExit(1)

r = cognee_client._client.get(f"/api/v1/datasets/{ds['id']}/data")
r.raise_for_status()
items = r.json()
print(f"{len(items)} stored documents in Cognee")
count = 0
for item in items:
    raw = cognee_client._client.get(f"/api/v1/datasets/{ds['id']}/data/{item['id']}/raw")
    if raw.status_code != 200:
        continue
    text = raw.text.strip().strip('"')
    if text.startswith("["):
        ledger.append(text)
        count += 1
print(f"ledger rebuilt with {count} entries -> {ledger._LEDGER}")
