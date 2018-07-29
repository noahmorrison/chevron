#!/usr/bin/python

import sys

try:
    import yaml as json
except ImportError:  # not tested
    import json

try:
    from .renderer import render
    from .metadata import version
except (ValueError, SystemError):  # python 2
    from renderer import render
    from metadata import version

import frontmatter


def main(template, data={}, stdin=sys.stdin, **kwargs):
    if template == '-':
        stream = stdin
    else:
        stream = open(template, 'r')

    with stream as template_file:

        if data != {}:
            data_file = open(data, 'r')
            data = json.load(data_file)
            data_file.close()
        else:
            data, template_file = frontmatter.parse(template_file.read())

        args = {
            'template': template_file,
            'data': data
        }

        args.update(kwargs)
        return render(**args)


def cli_main():
    """Render mustache templates using json files"""
    import argparse
    import os

    def is_file_or_pipe(arg):
        if arg == "-":
            return arg
        if not os.path.exists(arg) or os.path.isdir(arg):
            parser.error('The file {0} does not exist!'.format(arg))
        else:
            return arg

    def is_dir(arg):
        if not os.path.isdir(arg):
            parser.error('The directory {0} does not exist!'.format(arg))
        else:
            return arg

    parser = argparse.ArgumentParser(description=__doc__)

    parser.add_argument('-v', '--version', action='version',
                        version=version)

    parser.add_argument('template', help='The mustache file, "-" to read '
                                         'from stdin',
                        type=is_file_or_pipe)

    parser.add_argument('-d', '--data', dest='data',
                        help='The json data file, if you do not pass data, '
                             'you can use frontmatter in template',
                        default={})

    parser.add_argument('-p', '--path', dest='partials_path',
                        help='The directory where your partials reside',
                        type=is_dir, default='.')

    parser.add_argument('-e', '--ext', dest='partials_ext',
                        help='The extension for your mustache\
                              partials, \'mustache\' by default',
                        default='mustache')

    parser.add_argument('-l', '--left-delimiter', dest='def_ldel',
                        help='The default left delimiter, "{{" by default.',
                        default='{{')

    parser.add_argument('-r', '--right-delimiter', dest='def_rdel',
                        help='The default right delimiter, "}}" by default.',
                        default='}}')

    args = vars(parser.parse_args())

    try:
        sys.stdout.write(main(**args))
        sys.stdout.flush()
    except SyntaxError as e:
        print('Chevron: syntax error')
        print('    ' + '\n    '.join(e.args[0].split('\n')))
        exit(1)


if __name__ == '__main__':
    cli_main()
