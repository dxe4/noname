from functools import partial


def foo(x, z):
    print(x, z)


FOO = partial(foo, 0)
print(FOO((1,2,2)))
