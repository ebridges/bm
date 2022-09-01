import sys
from sys import argv, exit
from os.path import basename, expanduser
from os import environ
from argparse import ArgumentParser
from logging import basicConfig, DEBUG, INFO, info, error, debug, exception
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

    except Exception:
        exception(f'unable to bookmark URL: {url}')
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


def filename(type='html'):
    return f'{datetime.now():%Y%M%dT%H%m%S}.{type}'


def is_url(url):
    try:
        r = urlparse(url)
        return all([r.scheme, r.netloc])
    except BaseException:
        return False


def collect_editor_input(prompt):
    with NamedTemporaryFile(suffix='.tmp') as tmp:
        commented_prompt = f'# {prompt}\n#--------------------\n\n'
        tmp.write(commented_prompt.encode('utf-8'))
        tmp.flush()

        editor = environ.get('EDITOR', 'emacs')
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
    author = metadata.get('byline')
    title = metadata.get('title')
    if metadata.get('excerpt'):
        excerpt = sub('\n+', '\n', metadata.get('excerpt'))
    else:
        excerpt = None
    html = metadata.get('htmlContent', '')
    md = ''
    if html:
        md = convert_to_markdown(html)

    if edit:
        tag_string = input('Enter any tags, delimited by commas')
        tag_string = ''.join(
            tag_string.split()
        )  # strips all whitespace chars from string
        if tag_string:
            tags = tag_string.rstrip(',').split(',')
        else:
            tags = []

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
            'html': html,
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

    try:
        return loads(exec(cmd, f'Unable to format output of URL: {url}'))
    except Exception:
        return {}


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
    output = Popen(cmd, text=True, stdout=PIPE, stderr=PIPE)

    stdout, stderr = output.communicate()

    if output.returncode != 0:
        raise Exception(f'{errmsg}: the error received is "{stderr}"')

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
    DEFAULT_JOURNAL_DIR = '~/bookmarks'

    parser = ArgumentParser(prog=basename(argv[0]))
    parser.add_argument('-v', '--verbose', default=False, action='store_true')

    sp = parser.add_subparsers(title='Add a bookmark', dest='action')
    sp_add = sp.add_parser('add', help='Adds a bookmark.')
    sp_add.add_argument(
        '-u',
        '--url',
        dest='url',
        help='URL to bookmark.',
    )
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
    sp_add.add_argument(
        '-o',
        '--output',
        nargs='?',
        const=expanduser(DEFAULT_JOURNAL_DIR),
        help=f'''How to output bookmark.  Write to stdout if flag not present.
        If flag present without arg, write to [{DEFAULT_JOURNAL_DIR}].
        If flag present with arg, write to location specified by arg.''',
    )
    args = parser.parse_args()

    configure_logging(args.verbose)

    if args.action == 'add':
        if args.format:
            bm_file = filename(args.format)
        else:
            bm_file = filename()

        if args.output and args.output != '-':
            file = f'{args.output}/{bm_file}'
            sys.stdout = open(file, 'w')

        info(f'bookmarking {args.url}, {args.edit} to: {args.output}')
        result = add(args.url, args.format, args.edit, sys.stdout)
        exit(result if result else 0)

    parser.print_help()
    exit(2)


if __name__ == '__main__':
    app_run()
