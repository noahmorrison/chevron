#!/usr/bin/python

try:
    import yaml as json
except ImportError:  # not tested
    import json

try:
    from .renderer import render
except (ValueError, SystemError):  # python 2
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

    parser.add_argument('-v', '--version', action='version',
                        version='0.8.4')

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

    try:
        print(main(**args))
    except SyntaxError as e:
        print('Chevron: syntax error')
        print('    ' + '\n    '.join(e.args[0].split('\n')))
        exit(1)


if __name__ == '__main__':
    cli_main()
