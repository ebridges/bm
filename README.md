# bm

A command line tool for storing bookmarks along with information about them.

## Usage

```
usage: bm [-h] [-v] [-o [OUTPUT]] {add} ...

optional arguments:
  -h, --help            Show this help message and exit.
  -v, --verbose         Output verbose log messages.
  -o [OUTPUT], --output [OUTPUT]
                        How to output bookmark. Write to stdout if flag not present.
                        If flag present without arg, writes to a dated
                        file in your Dropbox folder.
                        If flag present with arg, write to location specified by arg.

Add a bookmark:
  {add}
    add                 Adds a bookmark.

positional arguments:
  URL                   URL to bookmark.

optional arguments:
  -e, --edit            In order to edit/add metainfo to bookmark before saving.
  -f [{md,html}], --format [{md,html}]
                        What format to write out bookmark data. Default: html
```

## Dependencies

* [pandoc](https://pandoc.org/installing.html)
* [readablilty](https://github.com/mozilla/readability)

## License

MIT
