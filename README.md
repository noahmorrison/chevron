[![Build Status](https://travis-ci.org/noahmorrison/chevron.svg?branch=master)](https://travis-ci.org/noahmorrison/chevron)


A python implementation of the [mustache templating language](http://mustache.github.io).

Why chevron?
------------

I'm glad you asked!

* chevron is fast!

Chevron runs in less than half the time of [pystache](http://github.com/defunkt/pystache) (Which is not even up to date on the spec).
And in about 70% the time of [Stache](https://github.com/hyperturtle/Stache) (A 'trimmed' version of mustache, also not spec compliant).

* chevron is pep8

The pep8 command is run by [travis](https://travis-ci.org/noahmorrison/chevron) to ensure consistency.

* chevron is spec compliant

Chevron passes all the unittests provided by the [spec](https://github.com/mustache/spec) (in every version listed below).

If you find a test that chevron does not pass, please [report it.](https://github.com/noahmorrison/chevron/issues/new)

* chevron is python 2 and 3 compliant

Python 2.6, 2.7, 3.2, 3.3, and 3.4 are all tested by travis.



USAGE
-----

Commandline usage: (if installed via pypi)
```
$ chevron [data file] [template file]
```

Python usage with strings
```
import chevron

chevron.render('Hello, {{ mustache }}!', {'mustache': 'World'})
```

Python usage with file
```
import chevron

with open('file.mustache', 'r') as f:
    chevron.render(f, {'mustache': 'World'})
```

Python usage with unpacking
```
import chevron

args = {
  template: 'Hello, {{ mustache }}!',

  data: {
    'mustache': 'World'
  }
}

chevron.render(**args)
```

chevron supports partials (via dictionaries)
```
import chevron

args = {
    template: 'Hello, {{> thing }}!',

    partials_dict: {
        'thing': 'World'
    }
}

chevron.render(**args)
```

chevron supports partials (via the filesystem)
```
import chevron

args = {
    template: 'Hello, {{> thing }}!',

    # defaults to .
    partials_path: 'partials/',

    # defaults to mustache
    partials_ext: 'ms',
}

# ./partials/thing.ms will be read and rendered
chevron.render(**args)
```

INSTALL
-------

- with git
```
$ git clone https://github.com/noahmorrison/chevron.git
```

or using submodules
```
$ git submodules add https://github.com/noahmorrison/chevron.git
```

Also available on pypi!

- with pip
```
$ pip install chevron
```



TODO
---

* get popular
* have people complain
* fix those complaints
