#!/usr/bin/python

import json

from sys import argv


class UnclosedSection(Exception):
    """Raised when you have unbalanced section tags"""
    pass


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
        template = template.read()
    except AttributeError:
        pass

    is_standalone = True
    open_sections = []
    l_del = '{{'
    r_del = '}}'
    while template:
        try:
            literal, template = template.split(l_del, 1)
        except ValueError:
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
            # If we have a third curly brace
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
                raise UnclosedSection()

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
        raise UnclosedSection()


def render(template='', data={}, partials_path='.', partials_ext='mustache',
           partials_dict={}, padding=0):
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
    padding       -- This is for padding partials, and shouldn't be used
                     (but can be if you really want to)

    Returns:
    A string containing the rendered template.
    """

    def html_escape(string):
        """HTML escape all of these " & < >"""

        html_codes = {
            '"': '&quot;',
            '<': '&lt;',
            '>': '&gt;',
        }

        # & must be handled first
        string = string.replace('&', '&amp;')
        for char in html_codes:
            string = string.replace(char, html_codes[char])
        return string

    def get_key(key):
        """Get a key from the current scope"""

        # If the key is a dot
        if key == '.':
            # Then just return the current scope
            return scopes[0]

        # Loop through the scopes
        for scope in scopes:
            try:
                # For every dot seperated key
                for key in key.split('.'):
                    # Move into the scope
                    scope = scope[key]
                # Return the last scope we got
                return scope
            except (TypeError, KeyError):
                # We couldn't find the key in the current scope
                # We'll try again on the next pass
                pass

        # We couldn't find the key in any of the scopes
        return ''

    def get_partial(name):
        """Load a partial"""
        try:
            # Maybe the partial is in the dictionary
            return partials_dict[name]
        except KeyError:
            # Nope...
            try:
                # Maybe it's in the file system
                path = partials_path + '/' + name + '.' + partials_ext
                with open(path, 'r') as partial:
                    return partial.read()

            except IOError:
                # Alright I give up on you
                return ''

    # If the template is a list
    if type(template) is list:
        # Then we don't need to tokenize it
        tokens = template
    else:
        # Otherwise make a generator
        tokens = tokenize(template)

    output = ''

    # If the data is a list
    if type(data) is list:
        # Then it's probably a list of scopes
        scopes = data
    else:
        # Otherwise it's a single scope
        scopes = [data]

    # Run through the tokens
    for tag, key in tokens:
        # Set the current scope
        current_scope = scopes[0]

        # If we're an end tag
        if tag == 'end':
            # Pop out of the latest scope
            scopes = scopes[1:]

        # If the current scope is falsy and not the only scope
        elif not current_scope and len(scopes) != 1:
            # If we're a section tag
            if tag == 'section':
                # Set it as the most recent scope
                scopes.insert(0, scope)

            # If we're an inverted section tag
            elif tag == 'inverted section':
                # Set the flipped scope as the most recent scope
                scopes.insert(0, not scope)

        # If we're a literal tag
        elif tag == 'literal':
            # Add padding to the key and add it to the output
            output += key.replace('\n', '\n' + (' ' * padding))

        # If we're a variable tag
        elif tag == 'variable':
            # Add the html escaped key to the output
            output += html_escape(str(get_key(key)))

        # If we're a no html escape tag
        elif tag == 'no escape':
            # Just lookup the key and add it
            output += str(get_key(key))

        # If we're a section tag
        elif tag == 'section':
            # Get the sections scope
            scope = get_key(key)

            # If the scope is a list
            if type(scope) is list:
                # Then we need to do some looping

                # Gather up all the tags inside the section
                tags = []
                for tag in tokens:
                    if tag == ('end', key):
                        break
                    tags.append(tag)

                # For every item in the scope
                for thing in scope:
                    # Append it as the most recent scope and render
                    new_scope = [thing] + scopes
                    output += render(tags, new_scope, partials_path,
                                     partials_ext, partials_dict)

            else:
                # Otherwise we're just a scope section
                scopes.insert(0, scope)

        # If we're an inverted section
        elif tag == 'inverted section':
            # Add the flipped scope to the scopes
            scope = get_key(key)
            scopes.insert(0, not scope)

        # If we're a partial
        elif tag == 'partial':
            # Load the partial
            partial = get_partial(key)

            # Find how much to pad the partial
            left = output.split('\n')[-1]
            part_padding = padding
            if left.isspace():
                part_padding += left.count(' ')

            # Render the partial
            part_out = render(partial, scopes, partials_path,
                              partials_ext, partials_dict, part_padding)

            # If the partial was indented
            if left.isspace():
                # then remove the spaces from the end
                part_out = part_out.rstrip(' ')

            # Add the partials output to the ouput
            output += part_out

    return output


def main(data, template, **kwargs):
    data = data
    template = template

    with open(template, 'r') as template_file:
        with open(data, 'r') as data_file:
            args = {
                'template': template_file,
                'data': json.load(data_file)
            }

            args.update(kwargs)
            return render(**args)

if __name__ == '__main__':
    print(main(argv[1], argv[2]))
