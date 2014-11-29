#!/usr/bin/python


#
# Python 2 and 3, module and script compatability
# If you know a better way please tell me :(
#

try:
    from .tokenizer import tokenize
except (ValueError, SystemError):
    from tokenizer import tokenize


try:  # python 2
    unicode
    python3 = False
except:
    def unicode(x, y):
        return x
    python3 = True


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

def render(template='', data={}, partials_path='.', partials_ext='mustache',
           partials_dict={}, padding=0, def_ldel='{{', def_rdel='}}',
           scopes=None):
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
            if type(key) != unicode:
                key = unicode(key, 'utf-8')
            output += key.replace('\n', '\n' + (' ' * padding))

        # If we're a variable tag
        elif tag == 'variable':
            # Add the html escaped key to the output
            thing = get_key(key)
            if type(thing) != unicode:
                thing = unicode(str(thing), 'utf-8')
            output += _html_escape(thing)

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
                    output += render(template=tags, scopes=new_scope,
                                     partials_path=partials_path,
                                     partials_ext=partials_ext,
                                     partials_dict=partials_dict,
                                     def_ldel=def_ldel, def_rdel=def_rdel)

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
