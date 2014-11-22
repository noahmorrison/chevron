#!/usr/bin/python

import json

from sys import argv

#
# Python 2 and 3, module and script compatability
# If you know a better way please tell me :(
#

try:
    from .tokenizer import tokenize
    from .renderer import render
except (ValueError, SystemError):
    from tokenizer import tokenize
    from renderer import render


def main(template, data={}, **kwargs):
    with open(template, 'r') as template_file:
        if data != {}:
            data_file = open(data, 'r')
            data = json.load(data_file)
            data_file.close()

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

    def is_file(arg):
        if not os.path.isfile(arg):
            parser.error('The file {0} does not exist!'.format(arg))
        else:
            return arg

    def is_dir(arg):
        if not os.path.isdir(arg):
            parser.error('The directory {0} does not exist!'.format(arg))
        else:
            return arg

    parser = argparse.ArgumentParser(description=__doc__)

    parser.add_argument('template', help='The mustache file',
                        type=is_file)

    parser.add_argument('-d', '--data', dest='data',
                        help='The json data file',
                        type=is_file, default={})

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

    print(main(**args))

if __name__ == '__main__':
    cli_main()
