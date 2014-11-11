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
            template.is_finished = True

        return data

    def grab_literal(until=None):
        until = until or l_del
        literal = get()
        while not template.is_finished:
            if literal[-len(until):] == until:
                return literal[:-len(until)]

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

    try:
        template = StringIO(template)
    except TypeError:
        pass

    template.is_finished = False
    is_standalone = True
    open_sections = []
    l_del = '{{'
    r_del = '}}'
    while not template.is_finished:
        literal = grab_literal()

        if literal != '':
            if literal.find('\n') != -1 or is_standalone:
                padding = literal.split('\n')[-1]
                if padding.isspace() or padding == '':
                    is_standalone = True
                else:
                    is_standalone = False

        if template.is_finished:
            yield ('literal', literal)
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
                dels = tag_key[:-1].strip().split(' ')
                l_del, r_del = dels[0], dels[-1]

        elif tag_type in ['section', 'inverted section']:
            open_sections.append(tag_key)

        elif tag_type == 'end':
            last_section = open_sections.pop()
            if tag_key != last_section:
                raise UnclosedSection()

        if is_standalone and tag_type not in ['variable', 'no escape']:
            until = grab_literal('\n')
            if until.isspace() or until == '':
                is_standalone = True
                literal = literal.rstrip(' ')

            else:
                is_standalone = False
                if template.is_finished:
                    template.is_finished = False

                template.seek(template.tell() - (len(until) + 1))

        if literal != '':
            yield ('literal', literal)

        if tag_type not in ['comment', 'set delimiter?']:
            yield (tag_type, tag_key)

    if open_sections:
        raise UnclosedSection()


def render(template, data, partials_path='.', partials_ext='mustache',
           partials_dict={}):
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
    partials_dict -- A python dictionary which will be search for partials
                     before the filesystem is. {'include': 'foo'} is the same
                     as a file called include.mustache
                     (defaults to {})

    Returns:
    A string containing the rendered template.
    """

    def html_escape(string):
        html_codes = {
            '"': '&quot;',
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
        if key == '.':
            return scopes[0]

        for scope in scopes:
            try:
                for key in key.split('.'):
                    scope = scope[key]
                return scope
            except (TypeError, KeyError):
                pass
        return ''

    def get_partial(name):
        try:
            return partials_dict[name]
        except KeyError:
            try:
                path = partials_path + '/' + name + '.' + partials_ext
                return open(path, 'r')
            except IOError:
                return StringIO(None)

    if type(template) is list:
        tokens = template
    else:
        tokens = tokenize(template)


    output = ''

    if type(data) is list:
        scopes = data
    else:
        scopes = [data]

    for tag, key in tokens:
        try:
            current_scope = scopes[0]
        except IndexError:
            current_scope = None

        if tag == 'end':
            scopes = scopes[1:]

        elif not current_scope and len(scopes) != 1:
            if tag == 'section':
                scopes.insert(0, scope)

            elif tag == 'inverted section':
                scopes.insert(0, not scope)

        elif tag == 'literal':
            output += key

        elif tag == 'variable':
            output += html_escape(str(get_key(key)))

        elif tag == 'no escape':
            output += str(get_key(key))

        elif tag == 'section':
            scope = get_key(key)

            if type(scope) is list:
                tags = []
                for tag in tokens:
                    if tag == ('end', key):
                        break
                    tags.append(tag)

                for thing in scope:
                    new_scope = [thing] + scopes
                    output += render(tags, new_scope, partials_path,
                                     partials_ext, partials_dict)

            else:
                scopes.insert(0, scope)

        elif tag == 'inverted section':
            scope = get_key(key)
            scopes.insert(0, not scope)

        elif tag == 'partial':
            partial = get_partial(key)
            output += render(partial, scopes, partials_path,
                             partials_ext, partials_dict)

        else:
            print('>>', tag)

    return output

if __name__ == '__main__':
    data = argv[1]
    template = argv[2]

    output = render(open(template, 'r'), json.load(open(data, 'r')))
    print(output)
