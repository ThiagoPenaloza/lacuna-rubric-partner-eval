#!/bin/zsh
set -e
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
echo "=== MICRO1 RUBRIC PARTNER EVAL ==="
echo
echo "[1/3] Validating the offline metagrader..."
python3 -B -m unittest discover -s eval -p 'test_*.py' -q
echo
echo "[2/3] Preserved local run: Ollama / qwen2.5:7b (English inputs)"
python3 - <<'PY'
import json
p = 'results/english_qwen2.5_7b/summary.json'
x = json.load(open(p))
print(f"tasks: {x['task_count']}")
print(f"valid protocol: {x['format_pass_rate']:.0%}")
print(f"full content proxy: {x['content_proxy_pass_rate']:.0%}")
PY
echo
echo "[3/3] Main artifacts"
find eval submission results/english_qwen2.5_7b -maxdepth 1 -type f | sort | sed 's#^#  #'
echo
echo "=== END: semantic content requires human adjudication ==="
