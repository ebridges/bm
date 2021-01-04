import sys
from sys import argv, exit
from os.path import basename, expanduser
from argparse import ArgumentParser
from logging import basicConfig, DEBUG, INFO, info, error, debug
from datetime import datetime
from urllib.parse import urlparse
from subprocess import Popen, PIPE, run, call
from json import loads
from re import sub
from uuid import uuid4
from tempfile import NamedTemporaryFile

from bm.formatter import formatter


def add(url, format, edit, output):
    debug(f'add({url}, {edit}) called.')
    if not is_url(url):
        error(f'Invalid URL: {url}')
        return 10

    try:
        bookmark_data = format_bookmark_data(url, edit)
        bookmark = format_bookmark(bookmark_data, format)
        write_bookmark(output, bookmark)

    except Exception as e:
        error(str(e))
        return 10


def write_bookmark(output, bookmark):
    debug('write_bookmark() called.')
    output.write(bookmark)


def format_bookmark(md, format):
    debug(f'format_bookmark("{md["title"]}") called.')

    if not md['location']:
        raise ValueError('Bookmark URL cannot be empty.')

    fmtr = formatter(format)
    bookmark = fmtr(md)

    return bookmark


def file(type='html'):
    return f'{datetime.now():%Y%M%dT%H%m%S}.{type}'


def is_url(url):
    try:
        r = urlparse(url)
        return all([r.scheme, r.netloc])
    except BaseException:
        return False


def collect_editor_input(
    prompt,
):
    with NamedTemporaryFile(suffix='.tmp') as tmp:
        commented_prompt = f'# {prompt}\n#--------------------\n\n'
        tmp.write(commented_prompt.encode('utf-8'))
        tmp.flush()

        editor = 'emacs'  # environ.get('EDITOR', 'emacs')
        output = call([editor, '+100', tmp.name])  # +100: go to end of file

        if output != 0:
            raise Exception('Error when collecting input from editor.')

        tmp.flush()
        tmp.seek(0)
        content = str(tmp.read(), encoding='utf-8')

        result = []
        for line in content.split('\n'):
            line.strip()
            if not line or line.startswith('#'):
                continue
            result.append(line)
        return result


def format_bookmark_data(url, edit):
    metadata = obtain_metadata(url)
    bookmark_date = datetime.now().isoformat('T', 'seconds')
    author = metadata['byline']
    title = metadata['title']
    excerpt = sub('\n+', '\n', metadata['excerpt'])
    md = convert_to_markdown(metadata['htmlContent'])

    if edit:
        tag_string = input('Enter any tags, delimited by commas')
        tag_string = ''.join(
            tag_string.split()
        )  # strips all whitespace chars from string
        tags = tag_string.split(',')

        quotes = collect_editor_input('Enter quotes, each on its own line.')

        comments = collect_editor_input(
            'Enter any comments, each one on its own line.'
        )  # noqa E501
    else:
        tags = []
        quotes = []
        comments = []

    return {
        'id': str(uuid4()),
        'location': url,
        'bookmark_date': bookmark_date,
        'author': author,
        'title': title,
        'excerpt': excerpt,
        'tags': tags,
        'quotes': quotes,
        'comments': comments,
        'content': {
            'md': md,
            'html': metadata['htmlContent'],
        },
    }


def obtain_metadata(url):
    debug(f'format_content({url}) called.')
    cmd = [
        'readable',
        '--quiet',
        '--json',
        '--low-confidence=exit',
        url,
    ]

    return loads(exec(cmd, f'Unable to format output of URL: {url}'))


def convert_to_markdown(html):
    debug('convert_to_markdown() called.')
    html = sub('\n+', '\n', html)
    cmd = ['pandoc', '--from', 'html', '--to', 'markdown']

    output = run(cmd, stdout=PIPE, input=bytes(html, encoding='utf-8'))

    if output.returncode != 0:
        raise Exception('Unable to convert html to markdown')

    return sub('\n+', '\n', output.stdout.decode('utf-8'))


def exec(cmd, errmsg):
    debug(f'exec({cmd}) called.')
    output = Popen(cmd, text=True, stdout=PIPE)

    stdout, _ = output.communicate()

    if output.returncode != 0:
        raise Exception(errmsg)

    return stdout


def configure_logging(verbose):
    if verbose:
        level = DEBUG
    else:
        level = INFO

    basicConfig(
        format='[%(asctime)s][%(levelname)s] %(message)s',
        datefmt='%Y/%m/%d %H:%M:%S',
        level=level,
    )


def app_run():
    DEFAULT_JOURNAL = f'~/Dropbox/Journals/bookmarks/{file()}'

    parser = ArgumentParser(prog=basename(argv[0]))
    parser.add_argument('-v', '--verbose', default=False, action='store_true')
    parser.add_argument(
        '-o',
        '--output',
        nargs='?',
        const=expanduser(DEFAULT_JOURNAL),
        help='How to output bookmark.  Write to stdout if flag not present.'
        + f'If flag present without arg, write to [{DEFAULT_JOURNAL}]; '
        + 'if flag present with arg, write to location specified by arg.',
    )
    sp = parser.add_subparsers(
        title='Add a bookmark',
        dest='action',
    )
    sp_add = sp.add_parser('add', help='Adds a bookmark.')
    sp_add.add_argument('url', metavar='URL', help='URL to bookmark.')
    sp_add.add_argument(
        '-e',
        '--edit',
        action='store_true',
        help='In order to edit/add metainfo to bookmark before saving.',
    )
    sp_add.add_argument(
        '-f',
        '--format',
        choices=['md', 'html'],
        const='html',
        default='html',
        nargs='?',
        help='What format to write out bookmark data. Default: html',
    )
    args = parser.parse_args()

    if args.output and args.output != '-':
        sys.stdout = open(args.output, 'w')

    configure_logging(args.verbose)

    if args.action == 'add':
        info(f'bookmarking {args.url}, {args.edit}')
        exit(add(args.url, args.format, args.edit, sys.stdout))

    parser.print_help()
    exit(2)


if __name__ == '__main__':
    app_run()
