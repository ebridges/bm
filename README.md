# bm

A command line tool for storing bookmarks along with information about them.

## Usage

```
usage: main.py [-h] [-v] [-e] [-f [{md,html}]] [-o [OUTPUT]] url

positional arguments:
  url

options:
  -h, --help            show this help message and exit
  -v, --verbose
  -e, --edit            In order to edit/add metainfo to bookmark before saving.
  -f [{md,html}], --format [{md,html}]
                        What format to write out bookmark data. Default: html
  -o [OUTPUT], --output [OUTPUT]
                        How to output bookmark. Write to stdout if flag not present. If flag present without arg, write
                        to [~/Documents/notebook/bookmarks]. If flag present with arg, write to location specified by
                        arg.
```

## Dependencies

These tools must be installed on your local system for this to function.

* [pandoc](https://pandoc.org/installing.html)
* [readability](https://github.com/mozilla/readability)
* [readability-cli](https://www.npmjs.com/package/readability-cli)

`$ brew install pandoc readability readability-cli`

## Installation

1. Download [latest release](https://github.com/ebridges/bm/releases/latest)
2. Unzip downloaded archive.
3. Move file named `bm` onto your path, e.g. `~/bin` or `/usr/local/bin`

## License

MIT
