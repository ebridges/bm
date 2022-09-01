from textwrap import dedent, fill


def formatter(type):
    if type == 'html':
        return html_formatter
    if type == 'md':
        return markdown_formatter
    raise Exception(f'Unrecognized format: {type}')


def html_formatter(md):
    keywords = ''
    tags = ''
    if md['tags']:
        tags_csv = ','.join(md['tags'])
        keywords = f'<meta name="keywords" content="{tags_csv}">'
        tags_li = ''.join(
            [
                f'\n                         <li class="tag">#{t}</li>'
                for t in md['tags']
            ]
        )  # noqa E501
        tags = f'''
                <dt>Tags</dt>
                <dd>
                    <ul style="list-style-type: none;">{tags_li}
                    </ul>
                </dd>'''

    title = ''
    title_html = ''
    if md['title']:
        title = md['title']
        title_html = f'''
                <dt>Title</dt>
                <dd class="title">{md['title']}</dd>'''

    comments = ''
    if md['comments']:
        cmts = ''.join(
            [
                f'\n                        <li class="comment">{c}</li>'
                for c in md['comments']
            ]
        )  # noqa E501
        comments = f'''
                <dt>Comments</dt>
                <dd>
                    <ul>{cmts}
                    </ul>
                </dd>'''

    quotes = ''
    if md['quotes']:
        qs = ''.join(
            [
                f'\n                    <blockquote class="quote">{q}</blockquote>'  # noqa E501
                for q in md['quotes']
            ]
        )  # noqa E501

        quotes = f'''
                <dt>Quotes</dt>
                <dd>{qs}
                </dd>'''

    description = ''
    description_html = ''
    if md['excerpt']:
        description = f'<meta name="description" content="{md["excerpt"]}">'
        description_html = f'''\n                <dt>Excerpt</dt>
                <dd>
                    <blockquote class="excerpt">{md["excerpt"]}</blockquote>
                </dd>'''

    author = ''
    if {md['author']}:
        author = f'<meta name="author" content="{md["author"]}">'

    location = ''
    location_html = ''
    if md['location']:
        location = f'<meta name="location" content="{md["location"]}">'
        location_html = f'''
                <dt>Location</dt>
                <dd>
                    <a href="{md['location']}" class="location">{md['location']}</a>
                </dd>'''  # noqa E501

    id = ''
    if md['id']:
        id = f'<meta name="id" content="{md["id"]}">'

    content = f'''<!DOCTYPE html>
    <html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en" lang="en">
        <head>
            <title>Bookmark of "{title}"</title>
            <meta http-equiv="Content-Type" content="text/html; charset=utf-8">
            {description}
            {keywords}
            {author}
            {location}
            {id}
            <style>
                body {{
                    font-family: helvetica, sans-serif;
                    color: #000000;
                    word-wrap: break-word;
                    -webkit-nbsp-mode: space;
                    line-break: auto;
                    white-space: pre-line;
                }}
                dt {{
                    font-size: 18px;
                    font-weight: bold;
                }}
                dd {{
                    margin-top: 5px;
                    margin-bottom: 20px;
                }}
                blockquote {{
                    font-size: 1em;
                    margin: 10px;
                    padding: 0 .75em 0 1em;
                    border-left: 1px solid #0033aa;
                }}
                ul,ol {{
                    padding-left: 1.5em;
                    text-indent: 0em;
                    margin-left: 0em;
                }}
                li {{
                    margin-top: .5em;
                    margin-bottom: 3px;
                }}
                pre {{
                    line-height: 1.45em;
                    background-color: inherit;
                    width: auto;
                    white-space: pre-wrap;
                    display: block;
                    margin: 2em 2em 2em 1em;
                    padding: 5px 0 5px 10px;
                    border-width: 1px;
                    border-color: #ddd;
                    border-style: solid;
                    padding: 6px 10px;
                    border-radius: 3px;
                    -moz-border-radius: 3px;
                    -webkit-border-radius: 3px;
                    word-wrap: break-word;
                }}
            </style>
        </head>
        <body>
            <dl>
                {title_html}{location_html}
                {description_html}{quotes}{comments}{tags}
                <dt>Content</dt>
                <dd>
                    <h1>{title}</h1>
                    {md['content']['html']}
                </dd>
                <dt>ID</dt>
                <dd>
                    {md['id']}
                </dd>
            </dl>
        </body>
    </html>
    '''

    return dedent(content)


def markdown_formatter(md):
    bookmark = ''
    bookmark = bookmark + f'Date: {md["bookmark_date"]}  \n'
    bookmark = bookmark + f'Location: {md["location"]}  \n'
    bookmark = bookmark + f'ID: {md["id"]}  \n'
    if md.get('title'):
        bookmark = bookmark + f'Title: {md["title"]}  \n'
    if md.get('author'):
        bookmark = bookmark + f'Author: {md["author"]}  \n'

    bookmark = bookmark + '\n'

    bookmark = bookmark + f'# Location\n\n<{md["location"]}>\n\n'

    if md.get('title'):
        bookmark = bookmark + f'## Title\n\n{md["title"]}\n\n'

    if md.get('excerpt'):
        bookmark = bookmark + f'## Excerpt\n\n{fill(md["excerpt"])}\n\n'

    if md['tags']:
        tags = ' '.join([f'#{t}' for t in md['tags']])
        bookmark = bookmark + f'## Tags\n\n{tags}\n\n'

    if md['quotes']:
        quotes = '\n\n'.join([f'> {q}' for q in md['quotes']])
        bookmark = bookmark + f'## Quotes\n\n{quotes}\n\n'

    if md['comments']:
        comments = '\n'.join([f'* {c}' for c in md['comments']])
        bookmark = bookmark + f'## Comments\n\n{comments}\n\n'

    return bookmark + f'## Content\n\n{md["content"]["md"]}\n'
