#!/usr/bin/env python3


import argparse
import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path


def local_iso_datetime(value):
    """Convert a Plex timestamp to ISO-8601 in the script runner's local time zone."""
    if value is None:
        return None

    if isinstance(value, (int, float)):
        dt = datetime.fromtimestamp(value, tz=timezone.utc)
    else:
        text = str(value).strip()
        try:
            dt = datetime.fromisoformat(text.replace("Z", "+00:00"))
        except ValueError:
            return text  # Preserve the value if its format is unrecognized.

        # Treat a datetime without an explicit time zone as UTC.
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)

    return dt.astimezone().isoformat(timespec="seconds")


def columns(db, table):
    """Convenience?"""
    return {row[1] for row in db.execute(f'PRAGMA table_info("{table}")')}


def query_db(db, exclude_show_season=False):
    """Query the given SQLite DB, return some results! Things get messy in
    here, best not to look too close..."""
    mi = columns(db, "metadata_items")
    settings = columns(db, "metadata_item_settings")
    media_items = columns(db, "media_items")
    media_parts = columns(db, "media_parts")

    required = {
        "metadata_items": (mi, {"id", "guid", "title"}),
        "metadata_item_settings": (
            settings,
            {"guid", "view_count", "last_viewed_at"},
        ),
        "media_items": (media_items, {"id", "metadata_item_id"}),
        "media_parts": (media_parts, {"media_item_id", "file"}),
    }
    for table, (found, needed) in required.items():
        missing = needed - found
        if missing:
            raise SystemExit(
                f"Expected columns missing from {table}: "
                f"{', '.join(sorted(missing))}"
            )

    # These fields may vary between Plex database versions.
    optional_fields = [
        "type",
        "year",
        "parent_title",
        "parent_index",
        "index",
        "originally_available_at",
        "duration",
    ]
    extra_fields = [
        f'mi."{field}" AS "{field}"' if field in mi else f'NULL AS "{field}"'
        for field in optional_fields
    ]

    # TV hierarchy is usually episode -> season -> show, linked by parent_id.
    if "parent_id" in mi:
        show_field = "COALESCE(grandparent.title, parent.title) AS show_name"
        hierarchy_joins = """
            LEFT JOIN metadata_items AS parent ON parent.id = mi.parent_id
            LEFT JOIN metadata_items AS grandparent ON grandparent.id = parent.parent_id
        """
    else:
        show_field = "NULL AS show_name"
        hierarchy_joins = ""

    exclude_clause = ""
    if exclude_show_season:
        exclude_clause = """
            AND mi.guid NOT LIKE 'plex://show%'
            AND mi.guid NOT LIKE 'plex://season%'
        """

    query = f"""
        SELECT
            mi.id AS metadata_id,
            mi.guid,
            mi.title,
            {", ".join(extra_fields)},
            {show_field},
            s.view_count,
            s.last_viewed_at
        FROM metadata_item_settings AS s
        JOIN metadata_items AS mi ON mi.guid = s.guid
        {hierarchy_joins}
        WHERE (
            COALESCE(s.view_count, 0) > 0
            OR s.last_viewed_at IS NOT NULL
        )
        {exclude_clause}
        ORDER BY s.last_viewed_at DESC
    """

    results = []
    for row in db.execute(query):
        item = dict(row)
        last_viewed = item.pop("last_viewed_at")

        item["watch_count"] = item.pop("view_count")
        item["last_watched"] = last_viewed
        item["last_watched_iso"] = local_iso_datetime(last_viewed)

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

    return results


def main():
    parser = argparse.ArgumentParser(description="Export Plex watch data to JSON.")
    parser.add_argument("database", help="Path to com.plexapp.plugins.library.db")
    parser.add_argument("-o", "--output", default="plex_watch_history.json")
    parser.add_argument(
        "-x", "--exclude-show-season",
        action="store_true",
        help="Exclude Plex show- and season-level entries (see README.md)",
    )
    args = parser.parse_args()

    db_path = Path(args.database).expanduser().resolve()
    if not db_path.is_file():
        raise SystemExit(f"Database not found: {db_path}")

    # Read-only connection; we don't modify the Plex database.
    db = sqlite3.connect(f"{db_path.as_uri()}?mode=ro", uri=True)
    db.row_factory = sqlite3.Row

    # Do the thing.
    results = query_db(db, args.exclude_show_season)

    db.close()

    output_path = Path(args.output).expanduser()
    output_path.write_text(
        json.dumps(results, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    print(f"Exported {len(results)} items to {output_path.resolve()}. Enjoy!")


if __name__ == "__main__":
    main()
