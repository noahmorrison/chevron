#!/usr/bin/python
# coding: utf-8

from sys import argv
from timeit import timeit

import chevron


def make_test(template=None, data=None, expected=None):
    def test():
        result = chevron.render(template, data)
        if result != expected:
            error = 'Test failed:\n-- got --\n{}\n-- expected --\n{}'
            raise Exception(error.format(result, expected))

    return test


def main(times):
    args = {
        'template': """\
{{# comments }}
<div class=comment>
    <span class=user>{{ user }}</span>
    <span class=body>{{ body }}</span>
    <span class=vote>{{ vote }}</span>
</div>
{{/ comments }}
""",
        'data': {
            'comments': [
                {'user': 'tommy',
                 'body': 'If this gets to the front page I\'ll eat my hat!',
                 'vote': 625},

                {'user': 'trololol',
                 'body': 'this',
                 'vote': -142},

                {'user': 'mctom',
                 'body': 'I wish thinking of test phrases was easier',
                 'vote': 83},

                {'user': 'the_thinker',
                 'body': 'Why is /u/trololol\'s post higher than ours?',
                 'vote': 36}
            ]
        },
        'expected': """\
<div class=comment>
    <span class=user>tommy</span>
    <span class=body>If this gets to the front page I'll eat my hat!</span>
    <span class=vote>625</span>
</div>
<div class=comment>
    <span class=user>trololol</span>
    <span class=body>this</span>
    <span class=vote>-142</span>
</div>
<div class=comment>
    <span class=user>mctom</span>
    <span class=body>I wish thinking of test phrases was easier</span>
    <span class=vote>83</span>
</div>
<div class=comment>
    <span class=user>the_thinker</span>
    <span class=body>Why is /u/trololol's post higher than ours?</span>
    <span class=vote>36</span>
</div>
"""
    }

    test = make_test(**args)

    print(timeit(test, number=times))


if __name__ == '__main__':
    try:
        main(int(argv[1]))
    except IndexError:
        main(10000)
