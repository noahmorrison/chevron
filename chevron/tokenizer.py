#!/usr/bin/python


def tokenize(template, def_ldel='{{', def_rdel='}}'):
    """Tokenize a mustache template

    Tokenizes a mustache template in a generator fashion,
    using file-like objects. It also accepts a string containing
    the template.


    Arguments:

    template -- a file-like object, or a string of a mustache template

    def_ldel -- The default left delimiter
                ("{{" by default, as in spec compliant mustache)

    def_rdel -- The default right delimiter
                ("}}" by default, as in spec compliant mustache)


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

    # If the template is a file-like object then read it
    try:
        template = template.read()
    except AttributeError:
        pass

    is_standalone = True
    open_sections = []
    l_del = def_ldel
    r_del = def_rdel

    while template:

        try:
            # Look for the next tag and move the template to it
            literal, template = template.split(l_del, 1)

        # There are no more tags in the template?
        except ValueError:
            # Then the rest of the template is a literal
            literal, template = (template, '')

        # If the template is completed
        if not template:
            # Then yield the literal and leave
            yield ('literal', literal)
            break

        # Checking if the next tag could be a standalone
        # If there is a newline, or the previous tag was a standalone
        if literal.find('\n') != -1 or is_standalone:
            padding = literal.split('\n')[-1]

            # If all the characters since the last newline are spaces
            if padding.isspace() or padding == '':
                # Then the next tag could be a standalone
                is_standalone = True
            else:
                # Otherwise it can't be
                is_standalone = False

        # Start work on the tag
        # Find the type meaning of the first character
        tag_type = tag_types.get(template[0], 'variable')

        # If the type is not a variable
        if tag_type != 'variable':
            # Then that first character is not needed
            template = template[1:]

        # Grab and strip the whitespace off the key
        tag_key, template = template.split(r_del, 1)
        tag_key = tag_key.strip()

        # If we might be a no html escape tag
        if tag_type == 'no escape?':
            # And we have a third curly brace
            # (And are using curly braces as delimiters)
            if template[0] == '}' and l_del == '{{' and r_del == '}}':
                # Then we are a no html escape tag
                template = template[1:]
                tag_type = 'no escape'

        # If we might be a set delimiter tag
        elif tag_type == 'set delimiter?':
            # If our key ends with an equal sign
            if tag_key.endswith('='):
                # Then get and set the delimiters
                dels = tag_key[:-1].strip().split(' ')
                l_del, r_del = dels[0], dels[-1]

        # If we are a section tag
        elif tag_type in ['section', 'inverted section']:
            # Then open a new section
            open_sections.append(tag_key)

        # If we are an end tag
        elif tag_type == 'end':
            # Then check to see if the last opened section
            # is the same as us
            last_section = open_sections.pop()
            if tag_key != last_section:
                # Otherwise we need to complain
                raise SyntaxError('End tag does not match '
                                  'the currently opened section')

        # Check right side if we might be a standalone
        if is_standalone and tag_type not in ['variable', 'no escape']:
            on_newline = template.split('\n', 1)

            # If the stuff to the right of us are spaces we're a standalone
            if on_newline[0].isspace() or not on_newline[0]:
                # Remove the stuff before the newline
                template = on_newline[-1]
                if tag_type != 'partial':
                    # Then we need to remove the spaces from the left
                    literal = literal.rstrip(' ')
            else:
                is_standalone = False

        # If we're a tag can't be a standalone
        else:
            is_standalone = False

        # Start yielding
        # Ignore literals that are empty
        if literal != '':
            yield ('literal', literal)

        # Ignore comments and set delimiters
        if tag_type not in ['comment', 'set delimiter?']:
            yield (tag_type, tag_key)

    # If there are any open sections when we're done
    if open_sections:
        # Then we need to complain
        raise SyntaxError("End of file while a section was open")
