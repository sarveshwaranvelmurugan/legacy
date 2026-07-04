from app import engines
import json

hyps = engines.pending_hypotheses()
hyp = hyps[-1]
print("Before:", hyp["status"], "confidence", hyp["confidence"])

updated = engines.respond_to_hypothesis(
    hyp["id"], "partial",
    context="I have actually been reading system design primer chapters offline, about 3 chapters this week, I just never logged it."
)
print("After:", updated["status"], "confidence", updated["confidence"])
print(json.dumps(updated, indent=2))
