from os.path import basename, expanduser
from sys import argv, exit
from argparse import ArgumentParser
from logging import basicConfig, DEBUG, INFO, info, error
from datetime import datetime
from urllib.parse import urlparse
from subprocess import Popen, PIPE, run
from json import loads
import re


DEFAULT_JOURNAL = expanduser('~/Dropbox/Journals/bookmarks')


def add(url):
    if not is_url(url):
        error(f'Invalid URL: {url}')
        return 10

    try:
        content = format_content(url)
        author = content['byline']
        title = content['title']
        description = re.sub('\n+', '\n', content['excerpt'])
        md = convert_to_markdown(content['htmlContent'])

        print(
            f'''
            author: {author}
            title: {title}
            excerpt:
            {description}
            markdown:
            {md}
            '''
        )
    except Exception as e:
        error(str(e))
        return 10


def file():
    return f'{datetime.now():%Y%M%dT%H%m%S}.md'


def is_url(url):
    try:
        r = urlparse(url)
        return all([r.scheme, r.netloc])
    except BaseException:
        return False


def format_content(url):
    cmd = [
        'readable',
        '--quiet',
        '--json',
        '--low-confidence=exit',
        url,
    ]

    return loads(exec(cmd, f'Unable to format output of URL: {url}'))


def convert_to_markdown(html):
    html = re.sub('\n+', '\n', html)
    cmd = ['pandoc', '--from', 'html', '--to', 'markdown']

    output = run(cmd, stdout=PIPE, input=bytes(html, encoding='utf-8'))

    if output.returncode != 0:
        raise Exception('Unable to convert html to markdown')

    return output.stdout.decode('utf-8')


def exec(cmd, errmsg):
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
    parser = ArgumentParser(prog=basename(argv[0]))
    parser.add_argument('-v', '--verbose', default=False, action='store_true')
    parser.add_argument(
        '-j',
        '--journal',
        nargs='?',
        const=DEFAULT_JOURNAL,
        help=f'Location of stored bookmarks. Default: {DEFAULT_JOURNAL}',
    )
    sp = parser.add_subparsers(
        title='Add a bookmark',
        dest='action',
    )
    sp_start = sp.add_parser('add', help='Adds a bookmark to the journal.')
    sp_start.add_argument('url', metavar='URL', help='URL to bookmark.')

    args = parser.parse_args()

    configure_logging(args.verbose)

    if args.action == 'add':
        info(f'bookmarking {args.url}')
        exit(add(args.url))

    parser.print_help()
    exit(2)


if __name__ == '__main__':
    app_run()
