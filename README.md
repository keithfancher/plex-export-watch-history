# plex_watch_history_export

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
$ python3 plex_watch_history_export.py com.plexapp.plugins.library.db

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
