def foo(a, b):
    return foo(bar(1)) # nofastlint: rules.match-foo, rules.match-bar