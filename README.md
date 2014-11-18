[![Build Status](https://travis-ci.org/noahmorrison/chevron.svg?branch=master)](https://travis-ci.org/noahmorrison/chevron)

A python implementation of the [mustache templating language](http://mustache.github.io).

Commandline usage:
```
    ./chevron.py [data file] [template file]
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



TODO
---

* get popular
* have people complain
* fix those complaints
