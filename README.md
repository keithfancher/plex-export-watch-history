# Plex export watch-history

Export your watch history from Plex! Outputs as `json`.

This is not so much for *migration* purposes -- plenty of tools exist for that
already. This is more for curiosity, data visibility, nostalgia,
sanity-checking... whatever!

Mostly, it's for my own personal use. I used Plex for over a decade, and it's
fun and interesting for me to explore this data in a more straightforward way
than digging through a SQLite database.

**NOTE:** This tool works as of now (November 2026), but of course I can't be
held responsible for future Plex schema changes, &c. YMMV!

## Usage

Run it, point it to (a copy of) your Plex SQLite database, e.g.:

```
$ python3 plex_export_watch_history.py com.plexapp.plugins.library.db

Exported 4490 items to plex_watch_history.json
```

Use `-h` for an explanation of command-line options. It's mostly
straightforward.

One option worth explaining: `-x, --exclude-show-season`. By default, Plex
keeps track of "watched" entries and counts for *seasons* and *shows* as a
whole, in addition to individual episodes. The script includes these entries
by default, though they're not super interesting or useful (to me at least).
You can exclude these with the `-x` option. (This is only relevant to TV show
entries, not movies.)

If you're curious, try the default output first. If the "show" and "season"
entries seem to spammy to you, use `-x`. Or keep both output `json` files,
just in case. 'Cause why not!

## Plex database location

...varies by OS/environment! Generally, it'll be something like:

```
[plex library location]/Library/Application Support/Plex Media Server/Plug-in Support/Databases/com.plexapp.plugins.library.db`
```

...where `[plex library location]`, again, varies by environment. On a Linux
machine, for example, it'll likely be in `/var/lib/plexmediaserver`.

## Output data format

Mostly just a column-dump -- nothin' fancy. Ordered from new-to-old.

Interesting fields will likely be: `title` (for shows or movies), `show_name`,
(for shows only), `file_paths`, `watch_count`, and the two `last_watched`
fields. (Plex only stores the most recent watch time, unfortunately.)

The `last_watched` field is just the value as it exists in the DB: a unix
timestamp. `last_watched_iso` is the same value, but formatted as an
[ISO-8601](https://en.wikipedia.org/wiki/ISO_8601) string, set to the time
zone of the machine running the script. This latter field is just for
human-readable convenience, easier `grep`ing, &c.
