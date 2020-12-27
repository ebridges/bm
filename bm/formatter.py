from textwrap import dedent, fill


def formatter(type):
    if type == 'html':
        return html_formatter
    if type == 'md':
        return markdown_formatter
    raise Exception(f'Unrecognized format: {type}')


def html_formatter(md):
    tags_csv = ''
    tags = ''
    if len(md['tags']):
        tags_csv = ','.join(md['tags'])
        tags_li = ''.join(
            list(
                map(
                    lambda t: f'\n             <li class="tag">#{t}</li>',
                    md['tags'],
                )
            )
        )
        tags = f'''
                <dt>Tags</dt>
                <dd>
                    <ul style="list-style-type: none;">{tags_li}
                    </ul>
                </dd>
        '''

    comments = ''
    if len(md['comments']):
        cmts = ''.join(
            list(
                map(
                    lambda c: f'\n            <li class="comment">{c}</li>',
                    md['comments'],
                )
            )
        )
        comments = f'''
                <dt>Comments</dt>
                <dd>
                    <ul>{cmts}
                    </ul>
                </dd>
        '''

    quotes = ''
    if len(md['quotes']):
        qs = ''.join(
            list(
                map(
                    lambda q: f'\n<blockquote class="quote">{q}</blockquote>',
                    md['quotes'],
                )
            )
        )
        quotes = f'''
                <dt>Quotes</dt>
                <dd>{qs}
                </dd>
        '''

    url = md['location']
    content = f'''
    <html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en" lang="en">
        <head>
            <title>2020-10-30</title>
            <meta http-equiv="Content-Type"
                  content="application/xhtml+xml; charset=utf-8">
            <meta name="description" content="{md['excerpt']}">
            <meta name="keywords" content="{tags_csv}">
            <meta name="author" content="{md['author']}">
            <meta name="location" content="{url}">
            <meta name="id" content="{md['id']}">
            <link rel="stylesheet" href="NBResources/CSS/bookmarks-style.css">
        </head>
        <body>
            <dl>
                <dt>Title</dt>
                <dd class="title">{md['title']}</dd>
                <dt>Location</dt>
                <dd>
                    <a href="{url}" class="location">{url}</a>
                </dd>
                <dt>Excerpt</dt>
                <dd>
                    <blockquote class="excerpt">{md['excerpt']}</blockquote>
                </dd>
                {quotes}
                {comments}
                {tags}
                <dt>Content</dt>
                <dd>
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
        tags = map(lambda t: f'#{t.strip()} ', md['tags'])
        bookmark = bookmark + f'## Tags\n\n{tags}\n\n'

    if md['quotes']:
        quotes = map(lambda q: f'> {q}\n', md['quotes'])
        bookmark = bookmark + f'## Quotes\n\n{quotes}\n\n'

    if md['comments']:
        comments = map(lambda c: f'* {c}\n', md['comments'])
        bookmark = bookmark + f'## Comments\n\n{comments}\n\n'

    return bookmark + f'## Content\n\n{md["content"]["md"]}\n'
