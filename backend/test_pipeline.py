"""End-to-end: CME -> cognee.remember -> cognify -> recall contradictions."""
from app import cme, cognee_client

reflection = (
    "I've been meaning to start system design prep but honestly haven't touched it. "
    "I did solve 2 leetcode mediums though, and I pushed the graph traversal module "
    "commit to the legacy repo. I keep telling people I'm preparing for the ServiceNow "
    "campus drive but I haven't done a single mock interview yet."
)

print("1) CME extraction...")
nodes = cme.extract_nodes(reflection, "2026-07-03")
strings = [cme.format_node_for_cognee(n) for n in nodes]
for s in strings:
    print("  ", s[:100])

print("2) remember() ...")
result = cognee_client.remember(strings)
print("   ingest status:", result["ingest"]["status"])

print("3) waiting for cognify...")
status = cognee_client.wait_for_processing()
print("   ", status)

print("4) recall() — contradiction query...")
answer = cognee_client.recall(
    "List every contradiction and unverified claim for user shanks, with dates and severity. "
    "Also list what actions shanks actually completed."
)
print(answer)
