"""One-shot CME test: raw reflection -> typed nodes -> memory strings."""
from app import cme

reflection = (
    "So today was kind of all over the place. I've been meaning to start system design "
    "prep but honestly haven't touched it. I did solve 2 leetcode mediums though, and I "
    "pushed the graph traversal module commit to the legacy repo. Also I keep telling "
    "people I'm preparing for the ServiceNow campus drive but I haven't done a single "
    "mock interview yet. Anyway the weather was nice."
)

nodes = cme.extract_nodes(reflection, "2026-07-03")
print(f"--- {len(nodes)} nodes extracted ---")
for n in nodes:
    print(cme.format_node_for_cognee(n))
