# -*- coding: utf-8 -*-

try:
    from .tokenizer import tokenize
except (ValueError, SystemError):  # python 2
    from tokenizer import tokenize


import sys
if sys.version_info[0] == 3:
    python3 = True

    def unicode(x, y):
        return x

else:  # python 2
    python3 = False


#
# Helper functions
#

def _html_escape(string):
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


def _get_key(key, scopes):
    """Get a key from the current scope"""

    # If the key is a dot
    if key == '.':
        # Then just return the current scope
        return scopes[0]

    # Loop through the scopes
    for scope in scopes:
        try:
            # For every dot seperated key
            for child in key.split('.'):
                # Move into the scope
                try:
                    # Try subscripting (Normal dictionaries)
                    scope = scope[child]
                except (TypeError, AttributeError):
                    # Try the dictionary (Complex types)
                    scope = scope.__dict__[child]

            # Return an empty string if falsy, with two exceptions
            # 0 should return 0, and False should return False
            if scope is 0:
                return 0
            if scope is False:
                return False

            return scope or ''
        except (AttributeError, KeyError):
            # We couldn't find the key in the current scope
            # We'll try again on the next pass
            pass

    # We couldn't find the key in any of the scopes
    return ''


def _get_partial(name, partials_dict, partials_path, partials_ext):
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


#
# The main rendering function
#

def render(template='', data={}, partials_path='.', partials_ext='mustache',
           partials_dict={}, padding=0, def_ldel='{{', def_rdel='}}',
           scopes=None):
    """Render a mustache template.

    Renders a mustache template with a data scope and partial capability.
    Given the file structure...
    ╷
    ├─╼ main.py
    ├─╼ main.ms
    └─┮ partials
      └── part.ms

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

    def_ldel      -- The default left delimiter
                     ("{{" by default, as in spec compliant mustache)

    def_rdel      -- The default right delimiter
                     ("}}" by default, as in spec compliant mustache)

    scopes        -- The list of scopes that get_key will look through


    Returns:

    A string containing the rendered template.
    """

    # If the template is a list
    if type(template) is list:
        # Then we don't need to tokenize it
        # But it does need to be a generator
        tokens = (token for token in template)
    else:
        # Otherwise make a generator
        tokens = tokenize(template, def_ldel, def_rdel)

    output = unicode('', 'utf-8')

    if scopes is None:
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
            if tag in ['section', 'inverted section']:
                # Set the most recent scope to a falsy value
                # (I heard False is a good one)
                scopes.insert(0, False)

        # If we're a literal tag
        elif tag == 'literal':
            # Add padding to the key and add it to the output
            if type(key) != unicode:
                key = unicode(key, 'utf-8')
            output += key.replace('\n', '\n' + (' ' * padding))

        # If we're a variable tag
        elif tag == 'variable':
            # Add the html escaped key to the output
            thing = _get_key(key, scopes)
            if thing is True and key == '.':
                # if we've coerced into a boolean by accident
                # (inverted tags do this)
                # then get the un-coerced object (next in the stack)
                thing = scopes[1]
            if type(thing) != unicode:
                thing = unicode(str(thing), 'utf-8')
            output += _html_escape(thing)

        # If we're a no html escape tag
        elif tag == 'no escape':
            # Just lookup the key and add it
            output += str(_get_key(key, scopes))

        # If we're a section tag
        elif tag == 'section':
            # Get the sections scope
            scope = _get_key(key, scopes)

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
                    rend = render(template=tags, scopes=new_scope,
                                  partials_path=partials_path,
                                  partials_ext=partials_ext,
                                  partials_dict=partials_dict,
                                  def_ldel=def_ldel, def_rdel=def_rdel)

                    if python3:
                        output += rend
                    else:  # python 2
                        output += rend.decode('utf-8')

            else:
                # Otherwise we're just a scope section
                scopes.insert(0, scope)

        # If we're an inverted section
        elif tag == 'inverted section':
            # Add the flipped scope to the scopes
            scope = _get_key(key, scopes)
            scopes.insert(0, not scope)

        # If we're a partial
        elif tag == 'partial':
            # Load the partial
            partial = _get_partial(key, partials_dict,
                                   partials_path, partials_ext)

            # Find how much to pad the partial
            left = output.split('\n')[-1]
            part_padding = padding
            if left.isspace():
                part_padding += left.count(' ')

            # Render the partial
            part_out = render(template=partial, partials_path=partials_path,
                              partials_ext=partials_ext,
                              partials_dict=partials_dict,
                              def_ldel=def_ldel, def_rdel=def_rdel,
                              padding=part_padding, scopes=scopes)

            # If the partial was indented
            if left.isspace():
                # then remove the spaces from the end
                part_out = part_out.rstrip(' ')

            # Add the partials output to the ouput
            if python3:
                output += part_out
            else:  # python 2
                output += part_out.decode('utf-8')

    if python3:
        return output
    else:  # python 2
        return output.encode('utf-8')
