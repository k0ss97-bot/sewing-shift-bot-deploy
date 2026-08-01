"""Run the read-only marketplace synchronization outside an HTTP request."""

import json

from marketplaces import sync_ozon


if __name__ == "__main__":
    result = sync_ozon()
    print(json.dumps(result, ensure_ascii=False))
    raise SystemExit(0 if result.get("ok") else 1)
