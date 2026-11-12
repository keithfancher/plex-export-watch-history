#!/usr/bin/env python3
import argparse
import json
import sqlite3
from pathlib import Path


def columns(db, table):
    return {row[1] for row in db.execute(f'PRAGMA table_info("{table}")')}


def main():
    parser = argparse.ArgumentParser(description="Export Plex watch data to JSON.")
    parser.add_argument("database", help="Path to com.plexapp.plugins.library.db")
    parser.add_argument("-o", "--output", default="plex_watch_history.json")
    args = parser.parse_args()

    db_path = Path(args.database).expanduser().resolve()
    if not db_path.is_file():
        raise SystemExit(f"Database not found: {db_path}")

    db = sqlite3.connect(f"{db_path.as_uri()}?mode=ro", uri=True)
    db.row_factory = sqlite3.Row

    mi = columns(db, "metadata_items")
    settings = columns(db, "metadata_item_settings")
    media_items = columns(db, "media_items")
    media_parts = columns(db, "media_parts")

    required = {
        "metadata_items": (mi, {"id", "guid", "title"}),
        "metadata_item_settings": (settings, {"guid", "view_count", "last_viewed_at"}),
        "media_items": (media_items, {"id", "metadata_item_id"}),
        "media_parts": (media_parts, {"media_item_id", "file"}),
    }
    for table, (found, needed) in required.items():
        missing = needed - found
        if missing:
            raise SystemExit(f"Expected columns missing from {table}: {', '.join(sorted(missing))}")

    optional_fields = [
        "type", "year", "parent_title", "parent_index", "index",
        "originally_available_at", "duration",
    ]
    extra_fields = [
        f'mi."{field}" AS "{field}"' if field in mi else f'NULL AS "{field}"'
        for field in optional_fields
    ]

    query = f"""
        SELECT mi.id AS metadata_id, mi.guid, mi.title,
               {", ".join(extra_fields)},
               s.view_count, s.last_viewed_at
        FROM metadata_item_settings AS s
        JOIN metadata_items AS mi ON mi.guid = s.guid
        WHERE COALESCE(s.view_count, 0) > 0 OR s.last_viewed_at IS NOT NULL
        ORDER BY s.last_viewed_at DESC
    """

    results = []
    for row in db.execute(query):
        item = dict(row)
        last_viewed = item.pop("last_viewed_at")
        item["watch_count"] = item.pop("view_count")
        item["last_watched"] = last_viewed

        paths = db.execute(
            """
            SELECT DISTINCT mp.file
            FROM media_items AS med
            JOIN media_parts AS mp ON mp.media_item_id = med.id
            WHERE med.metadata_item_id = ?
            ORDER BY mp.file
            """,
            (item["metadata_id"],),
        ).fetchall()
        item["file_paths"] = [p["file"] for p in paths if p["file"]]

        results.append(item)

    db.close()
    output = Path(args.output).expanduser()
    output.write_text(json.dumps(results, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Exported {len(results)} items to {output.resolve()}")


if __name__ == "__main__":
    main()
