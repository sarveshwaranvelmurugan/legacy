"""Rebuild the local ledger from Cognee's raw stored documents."""
from app import cognee_client, config, ledger

datasets = cognee_client.list_datasets()
ds = next(d for d in datasets if d["name"] == config.DATASET_NAME)
r = cognee_client._client.get(f"/api/v1/datasets/{ds['id']}/data")
r.raise_for_status()
items = r.json()
print(f"{len(items)} stored documents")
count = 0
for item in items:
    raw = cognee_client._client.get(f"/api/v1/datasets/{ds['id']}/data/{item['id']}/raw")
    if raw.status_code != 200:
        continue
    text = raw.text.strip().strip('"')
    if text.startswith("["):
        ledger.append(text)
        count += 1
print(f"backfilled {count} entries")
