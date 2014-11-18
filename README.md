A python implementation of the [mustache templating language](http://mustache.github.io).

Commandline usage:
```
    ./entei.py [data file] [template file]
```

Python usage with strings
```
import entei

entei.render('Hello, {{ mustache }}!', {'mustache': 'World'})
```

Python usage with file
```
import entei

with open('file.mustache', 'r') as f:
    entei.render(f, {'mustache': 'World'})
```

Python usage with unpacking
```
import entei

args = {
  template: 'Hello, {{ mustache }}!',

  data: {
    'mustache': 'World'
  }
}

entei.render(**args)
```



TODO
---

* get popular
* have people complain
* fix those complaints
