from app import engines

print("=== CONTRADICTION ENGINE ===")
print(engines.contradiction_engine()[:800])
print()
print("=== BEHAVIORAL INFERENCE ===")
hyp = engines.behavioral_inference()
import json; print(json.dumps(hyp, indent=2))
