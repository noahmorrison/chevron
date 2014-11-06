#!/usr/bin/python

import json

from sys import argv
from io import StringIO


def tokenize(template):
    """Tokenize a mustache template

    Tokenizes a mustache template in a generator fashion,
    using file-like objects. It also accepts a string containing
    the template.

    Arguments:
    template -- a file-like object, or a string of a mustache template

    Returns:
    A generator of mustache tags in the form of a tuple
    -- (tag_type, tag_key)

    Where tag_type is one of:
     * literal
     * section
     * inverted section
     * end
     * partial
     * no escape
    And tag_key is either the key or in the case of a literal tag,
    the literal itself.
    """

    class UnclosedSection(Exception):
        pass

    def get(amount=1):
        data = template.read(amount)
        if len(data) != amount:
            template.close()

        return data

    def grab_literal(until=None):
        until = until or l_del
        literal = get()
        while not template.closed:
            if literal[-2:] == until:
                return literal[:-2]

            literal += get()

        return literal

    tag_types = {
        '!': 'comment',
        '#': 'section',
        '^': 'inverted section',
        '/': 'end',
        '>': 'partial',
        '=': 'set delimiter?',
        '{': 'no escape?',
        '&': 'no escape'
    }

    if type(template) is str:
        template = StringIO(template)

    open_sections = []
    l_del = '{{'
    r_del = '}}'
    while not template.closed:
        literal = grab_literal()

        if literal != '':
            yield ('literal', literal)

        if template.closed:
            break

        tag_key = get(1)
        tag_type = tag_types.get(tag_key, 'variable')
        if tag_type != 'variable':
            tag_key = ''

        tag_key += grab_literal(r_del)
        tag_key = tag_key.strip()

        if tag_type == 'no escape?':
            if get(1) == '}':
                tag_type = 'no escape'
            else:
                template.seek(template.tell() - 1)

        elif tag_type == 'set delimiter?':
            if tag_key[-1] == '=':
                l_del, r_del = tag_key[:-1].split(' ')
                get(2)
                continue

        elif tag_type in ['section', 'inverted section']:
            open_sections.append(tag_key)

        elif tag_type == 'end':
            last_section = open_sections.pop()
            if tag_key != last_section:
                raise UnclosedSection()

        if tag_type != 'comment':
            yield (tag_type, tag_key)

    if open_sections:
        raise UnclosedSection()


def render(template, data, partials_path='.', partials_ext='mustache'):
    """Render a mustache template.

    Renders a mustache template with a data scope and partial capability.
    Given the file structure...
    .
    |- main.py
    |- main.ms
    |- partials
     |- part.ms

    then main.py would make the following call:

    render(open('main.ms', 'r'), {...}, 'partials', 'ms')

    Arguments:
    template      -- A file-like object or a string containing the template
    data          -- A python dictionary with your data scope
    partials_path -- The path to where your partials are stored
                     (defaults to '.')
    partials_ext  -- The extension that you want the parser to look for
                     (defaults to 'mustache')

    Returns:
    A string containing the rendered template.
    """

    def html_escape(string):
        html_codes = {
            '"': '$quot;',
            '&': '&amp;',
            '<': '&lt;',
            '>': '&gt;',
        }

        def escape_char(char):
            return html_codes.get(char, char)

        try:
            return ''.join(map(escape_char, string))
        except TypeError:
            return ''

    def get_key(key):
        for scope in scopes:
            try:
                for key in key.split('.'):
                    scope = scope[key]
                return scope
            except (TypeError, KeyError):
                pass

    def get_partial(path):
        return partials_path + '/' + path + '.' + partials_ext

    tokens = tokenize(template)

    output = ''
    if type(data) is list:
        scopes = data
    else:
        scopes = [data]

    for tag, key in tokens:
        if tag == 'end':
            scopes = scopes[1:]

        elif not scopes[0] and len(scopes) != 1:
            pass

        elif tag == 'literal':
            output += key

        elif tag == 'variable':
            output += html_escape(get_key(key))

        elif tag == 'no escape':
            output += get_key(key)

        elif tag == 'section':
            scope = get_key(key)
            scopes.insert(0, scope)

        elif tag == 'inverted section':
            scope = get_key(key)
            scopes.insert(0, not scope)

        elif tag == 'partial':
            partial = get_partial(key)
            output += render(open(partial, 'r'), scopes)

        else:
            print('>>', tag)

    return output

if __name__ == '__main__':
    data = argv[1]
    template = argv[2]

    output = render(open(template, 'r'), json.load(open(data, 'r')))
    print(output)
