"""Seed 30 days of realistic demo history into the Legacy graph.

One CME call per reflection (~16 Haiku calls, ~5 cents total), then a single
batched remember() so cognify runs once.
"""
from app import cme, cognee_client

REFLECTIONS = [
    ("2026-06-03", "Setting my goals for the summer. One: learn system design properly, "
     "I want to be interview-ready by end of August. Two: DSA practice, at least 3 leetcode "
     "problems a week. Three: prepare for the ServiceNow campus drive, which means mock "
     "interviews. Four: build my hackathon portfolio, I want to win at least one this summer. "
     "Five: get into AI research, I should be reading papers regularly."),
    ("2026-06-05", "Solved 3 leetcode problems today, two mediums and one easy. Arrays and "
     "sliding window. Also registered for the CodeCrafters hackathon happening next weekend."),
    ("2026-06-08", "Spent the whole weekend building for CodeCrafters. We made a realtime "
     "collab whiteboard. Pushed like 14 commits. Didn't sleep much but we made the finals!"),
    ("2026-06-09", "We won second place at CodeCrafters! Prize was 10k INR split among the "
     "team. I'm getting good at this hackathon thing honestly."),
    ("2026-06-11", "Did 2 leetcode mediums on trees. I am being pretty consistent with DSA "
     "I think. Haven't started system design yet but I'll get to it this weekend for sure."),
    ("2026-06-14", "Busy week with college stuff. I keep saying I'm preparing for the "
     "ServiceNow drive but honestly I haven't done a single mock interview yet. I did watch "
     "one system design video on YouTube about load balancers, does that count?"),
    ("2026-06-16", "Solved 3 leetcode problems, dynamic programming set. DP is finally "
     "clicking. Also signed up for the WeMakeDevs hackathon at the end of the month."),
    ("2026-06-18", "Posted on LinkedIn about our CodeCrafters win, it got 200+ reactions. "
     "A senior from Microsoft commented. Networking is going well I feel."),
    ("2026-06-20", "I'm a consistent system design learner now — I read half a chapter of "
     "Designing Data-Intensive Applications today. First real system design study session "
     "this month if I'm honest."),
    ("2026-06-22", "3 more leetcode problems, graphs. Also started sketching ideas for the "
     "WeMakeDevs hackathon. I want to build something with AI memory. Still no mock "
     "interviews. The ServiceNow drive is in September, feels far but I know it isn't."),
    ("2026-06-24", "Spent 4 hours planning the hackathon project architecture. Wrote a full "
     "design doc. This is the most excited I've been about a project in months."),
    ("2026-06-26", "Two leetcode mediums today. Also I keep telling myself I'll read one "
     "research paper a week to get into AI research but I haven't opened a single paper "
     "since I set that goal. Not one."),
    ("2026-06-28", "Deep in hackathon prep. Set up the Cognee cloud account, tested the "
     "APIs, pushed initial commits to the legacy repo. DSA taking a backseat this week."),
    ("2026-06-30", "Hackathon started yesterday. Built the memory distillation prototype, "
     "pushed 6 commits. I skipped leetcode this week entirely but the hackathon is worth it."),
    ("2026-07-01", "More hackathon building, the contradiction engine works now. Also my "
     "mom asked when my campus placements start and I realized I still haven't done any "
     "interview prep. September is two months away. That scared me a bit."),
    ("2026-07-02", "Pushed the graph traversal module to the legacy repo. The project is "
     "coming together. I read one page of DDIA before falling asleep, so system design is "
     "technically not dead."),
]

all_strings = []
for d, text in REFLECTIONS:
    nodes = cme.extract_nodes(text, d)
    strings = [cme.format_node_for_cognee(n) for n in nodes]
    all_strings.extend(strings)
    print(f"{d}: {len(nodes)} nodes")

print(f"\nTotal: {len(all_strings)} memory strings. Ingesting...")
result = cognee_client.remember(all_strings)
print("ingest:", result["ingest"]["status"])
print("waiting for cognify (this can take a few minutes)...")
print(cognee_client.wait_for_processing(timeout_s=900))
