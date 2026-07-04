#!/bin/zsh
# Legacy — Cognee Cloud smoke test: ingest typed nodes -> cognify -> recall
set -e
export PATH=/usr/bin:/bin:/usr/sbin:/sbin:$PATH
source "$(dirname "$0")/../.env"
HOST=${COGNEE_BASE_URL#https://}
RESOLVE=(--resolve "$HOST:443:54.197.228.131")

cognee() {
  local method=$1 path=$2 data=$3
  if [[ -n "$data" ]]; then
    /usr/bin/curl -s -m 280 "${RESOLVE[@]}" -X "$method" "$COGNEE_BASE_URL$path" \
      -H "X-Api-Key: $COGNEE_API_KEY" -H "Content-Type: application/json" -d "$data"
  else
    /usr/bin/curl -s -m 280 "${RESOLVE[@]}" -X "$method" "$COGNEE_BASE_URL$path" \
      -H "X-Api-Key: $COGNEE_API_KEY"
  fi
}

case "$1" in
  add)
    cognee POST /api/v1/add_text '{
      "textData": [
        "[GOAL] user shanks committed to goal: Learn System Design. domain: engineering. committed on 2026-06-03. status OPEN. verified false.",
        "[CLAIM] user shanks claims: I am consistently practicing system design. stated on 2026-06-10. confidence 0.3. verified false. no supporting evidence yet.",
        "[ACTION] user shanks did: Completed 2 LeetCode medium problems. linked goal: DSA preparation. date 2026-06-28. confidence 0.8.",
        "[ACTION] user shanks did: Won college hackathon with sign language project. linked goal: Hackathon portfolio. date 2026-06-15. confidence 0.9.",
        "[EVIDENCE] user shanks source github. value: commit Add graph traversal module. repo legacy. date 2026-07-01. verified true."
      ],
      "datasetName": "legacy_test",
      "nodeSet": ["legacy_nodes"]
    }' | python3 -m json.tool
    ;;
  cognify)
    cognee POST /api/v1/cognify '{"datasets": ["legacy_test"], "runInBackground": true}' | python3 -m json.tool
    ;;
  status)
    cognee GET "/api/v1/datasets/status" | python3 -m json.tool
    ;;
  recall)
    cognee POST /api/v1/recall '{
      "query": "Which claims by shanks have no supporting evidence, and how many days old are they? What goals were committed and when?",
      "datasets": ["legacy_test"],
      "searchType": "GRAPH_COMPLETION",
      "topK": 15
    }' | python3 -m json.tool
    ;;
  datasets)
    cognee GET /api/v1/datasets/ | python3 -m json.tool
    ;;
  *)
    echo "usage: $0 add|cognify|status|recall|datasets"
    ;;
esac
