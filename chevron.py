#!/usr/bin/python

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
            raise EOFError()

        return data

    def peek(ahead=0, amount=1):
        current = template.tell()
        template.seek(current + ahead)
        data = template.read(amount)
        template.seek(current)
        if len(data) != amount:
            raise EOFError()
        return data

    def grab_literal(until=None):
        until = until or l_del
        literal = get()
        while literal[-2:] != until:
            literal += get()

        return literal[:-2]

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
        try:
            literal = grab_literal()
        except EOFError:
            return

        if literal:
            yield ('literal', literal)

        tag_type = tag_types.get(peek(0, 1), 'variable')
        if tag_type != 'variable':
            template.seek(template.tell() + 1)

        tag_key = grab_literal(r_del).strip()

        if tag_type == 'no escape?':
            if peek(0, 1) == '}':
                tag_type = 'no escape'
                get(1)

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


if __name__ == '__main__':
    data = argv[1]
    template = argv[2]

    tokens = tokenize(open(template, 'r'))

    for token in tokens:
        print(token)
