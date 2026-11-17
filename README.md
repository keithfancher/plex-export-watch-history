# Export Plex watch-history

Export your watch-history from Plex! Outputs as `json`.

This is not so much for *migration* purposes --
[plenty](https://github.com/wilmardo/migrate-plex-to-jellyfin) of
[tools](https://github.com/luigi311/JellyPlex-Watched) exist for that already.
This is more for curiosity, data visibility, nostalgia, or sanity-checking a
migration.

Mostly, it's for my own personal use. I used Plex for over a decade, and it's
fun and interesting for me to explore this data in a more straightforward way
than digging through a SQLite database. (It was also useful to sanity-check my
own migration to Jellyfin.)

**NOTE:** This tool works as of now (November 2026), but of course I can't be
held responsible for future Plex schema changes, &c. YMMV!

## Usage

Run it, point it to (a copy of) your Plex SQLite database, e.g.:

```sh
$ python3 plex_export_watch_history.py com.plexapp.plugins.library.db

Exported 4490 items to plex_watch_history.json. Enjoy!
```

Use `-h` for an explanation of command-line options. It's mostly
straightforward.

One option worth mentioning: `-x, --exclude-show-season`. By default, Plex
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
[plex library location]/Library/Application Support/Plex Media Server/Plug-in Support/Databases/com.plexapp.plugins.library.db
```

...where `[plex library location]`, again, varies by environment. On a Linux
machine, for example, it'll likely be in `/var/lib/plexmediaserver`.

## Output data format

Mostly just a column-dump, after doing all the annoying `JOIN`ing and
`COALESCE`ing and filtering and so on. Ordered from new-to-old.

Here's a sample movie entry:
```json
  {
    "metadata_id": 251,
    "guid": "com.plexapp.agents.themoviedb://8420?lang=en",
    "title": "And God Created Woman",
    "type": null,
    "year": 1956,
    "parent_title": null,
    "parent_index": null,
    "index": 1,
    "originally_available_at": -413164800,
    "duration": 5700000,
    "show_name": null,
    "watch_count": 1,
    "last_watched": 1430612724,
    "last_watched_iso": "2015-05-02T17:25:24-07:00",
    "file_paths": [
      "/media/Film/And God Created Woman (Roger Vadim, 1956)/And God Created Woman (1956).mp4"
    ]
  },
```

And here's an episode of a TV show:
```json
  {
    "metadata_id": 714,
    "guid": "plex://episode/5d9c0d8b4eefaa001f60adda",
    "title": "Black Widower",
    "type": null,
    "year": 1992,
    "parent_title": null,
    "parent_index": null,
    "index": 21,
    "originally_available_at": 702777600,
    "duration": 1380000,
    "show_name": "The Simpsons",
    "watch_count": 2,
    "last_watched": 1564467141,
    "last_watched_iso": "2019-07-29T23:12:21-07:00",
    "file_paths": [
      "/media/Television/Simpsons/Season 03/The Simpsons - s03e21 - Black Widower.mkv"
    ]
  },
```

Interesting fields will likely be: `title` (for shows or movies), `show_name`,
(for shows only), `file_paths`, `watch_count`, and the two `last_watched`
fields. (Plex only stores the most recent watch time, unfortunately.)

The `last_watched` field is just the value as it exists in the DB: a unix
timestamp. `last_watched_iso` is the same value, but formatted as an
[ISO-8601](https://en.wikipedia.org/wiki/ISO_8601) string, set to the time
zone of the machine running the script. This latter field is just for
human-readable convenience, easier `grep`ing, &c.
