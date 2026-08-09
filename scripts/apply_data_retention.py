#!/usr/bin/env python3
"""Migrate private photos and apply the configured lifecycle policy."""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def parse_args():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply", action="store_true", help="Delete expired photo payloads; default is dry-run.")
    parser.add_argument("--skip-migration", action="store_true", help="Do not move legacy base64 photos into private storage.")
    return parser.parse_args()


def main():
    args = parse_args()
    from database import init_db, migrate_legacy_defect_photos, purge_expired_defect_photos

    init_db()
    retention_days = int(os.environ.get("DEFECT_PHOTO_RETENTION_DAYS", "365") or 365)
    migration = {"skipped": True} if args.skip_migration else migrate_legacy_defect_photos()
    lifecycle = purge_expired_defect_photos(retention_days, dry_run=not args.apply)
    print(json.dumps({"ok": True, "migration": migration, "lifecycle": lifecycle}, ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()
