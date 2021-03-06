import math
from datetime import date, datetime

import pytest

from yui.apps.compute.calc import BadSyntax, Decimal as D, Evaluator, calculate


class GetItemSpy:
    def __init__(self):
        self.queue = []

    def __getitem__(self, item):
        self.queue.append(item)


def test_annassign():
    e = Evaluator()

    err = 'You can not use annotation syntax'
    with pytest.raises(BadSyntax, match=err):
        e.run('a: int = 10')

    assert 'a' not in e.symbol_table


def test_assert():
    e = Evaluator()
    err = 'You can not use assertion syntax'
    with pytest.raises(BadSyntax, match=err):
        e.run('assert True')

    with pytest.raises(BadSyntax, match=err):
        e.run('assert False')


def test_assign():
    e = Evaluator()
    e.run('a = 1 + 2')
    assert e.symbol_table['a'] == 3
    e.run('x, y = 10, 20')
    assert e.symbol_table['x'] == 10
    assert e.symbol_table['y'] == 20

    e.symbol_table['dt'] = datetime.now()
    err = 'This assign method is not allowed'
    with pytest.raises(BadSyntax, match=err):
        e.run('dt.year = 2000')


def test_asyncfor():
    e = Evaluator()
    e.symbol_table['r'] = 0
    err = 'You can not use `async for` loop syntax'
    with pytest.raises(BadSyntax, match=err):
        e.run('''
async for x in [1, 2, 3, 4]:
    r += x

''')
    assert e.symbol_table['r'] == 0


def test_asyncfunctiondef():
    e = Evaluator()
    err = 'Defining new coroutine via def syntax is not allowed'
    with pytest.raises(BadSyntax, match=err):
        e.run('''
async def abc():
    pass

''')
    assert 'abc' not in e.symbol_table


def test_asyncwith():
    e = Evaluator()
    e.symbol_table['r'] = 0
    err = 'You can not use `async with` syntax'
    with pytest.raises(BadSyntax, match=err):
        e.run('''
async with x():
    r += 100

''')
    assert e.symbol_table['r'] == 0


def test_attribute():
    e = Evaluator()
    e.symbol_table['dt'] = datetime.now()
    e.run('x = dt.year')
    assert e.symbol_table['x'] == e.symbol_table['dt'].year

    err = 'You can not access `test_test_test` attribute'
    with pytest.raises(BadSyntax, match=err):
        e.run('y = dt.test_test_test')

    assert 'y' not in e.symbol_table

    err = "You can not access `asdf` attribute"
    with pytest.raises(BadSyntax, match=err):
        e.run('z = x.asdf')

    e.symbol_table['math'] = math
    err = "You can not access `__module__` attribute"
    with pytest.raises(BadSyntax, match=err):
        e.run('math.__module__')

    e.symbol_table['datetime'] = datetime
    err = "You can not access `test_test` attribute"
    with pytest.raises(BadSyntax, match=err):
        e.run('datetime.test_test')


def test_augassign():
    e = Evaluator()
    e.symbol_table['a'] = 0
    e.run('a += 1')
    assert e.symbol_table['a'] == 1
    e.symbol_table['l'] = [1, 2, 3, 4]
    e.run('l[0] -= 1')
    assert e.symbol_table['l'] == [0, 2, 3, 4]

    err = 'This assign method is not allowed'
    with pytest.raises(BadSyntax, match=err):
        e.run('l[2:3] += 20')

    e.symbol_table['dt'] = datetime.now()
    err = 'This assign method is not allowed'
    with pytest.raises(BadSyntax, match=err):
        e.run('dt.year += 2000')


def test_await():
    e = Evaluator()
    err = 'You can not await anything'
    with pytest.raises(BadSyntax, match=err):
        e.run('r = await x()')
    assert 'r' not in e.symbol_table


def test_binop():
    e = Evaluator()
    assert e.run('1 + 2') == 1 + 2
    assert e.run('3 & 2') == 3 & 2
    assert e.run('1 | 2') == 1 | 2
    assert e.run('3 ^ 2') == 3 ^ 2
    assert e.run('3 / 2') == 3 / 2
    assert e.run('3 // 2') == 3 // 2
    assert e.run('3 << 2') == 3 << 2
    with pytest.raises(TypeError):
        e.run('2 @ 3')
    assert e.run('3 * 2') == 3 * 2
    assert e.run('33 % 4') == 33 % 4
    assert e.run('3 ** 2') == 3 ** 2
    assert e.run('100 >> 2') == 100 >> 2
    assert e.run('3 - 1') == 3 - 1


def test_boolop():
    e = Evaluator()
    assert e.run('True and False') == (True and False)
    assert e.run('True or False') == (True or False)


def test_break():
    e = Evaluator()
    e.run('break')
    assert e.current_interrupt.__class__.__name__ == 'Break'


def test_bytes():
    e = Evaluator()
    assert e.run('b"asdf"') == b'asdf'
    e.run('a = b"asdf"')
    assert e.symbol_table['a'] == b'asdf'


def test_call():
    e = Evaluator()
    e.symbol_table['date'] = date
    e.run('x = date(2019, 10, day=7)')
    assert e.symbol_table['x'] == date(2019, 10, day=7)

    e.symbol_table['math'] = math
    e.run('y = math.sqrt(121)')
    assert e.symbol_table['y'] == math.sqrt(121)

    e.symbol_table['datetime'] = datetime
    e.run('z = datetime.now().date()')
    assert e.symbol_table['z'] == datetime.now().date()


def test_classdef():
    e = Evaluator()
    err = 'Defining new class via def syntax is not allowed'
    with pytest.raises(BadSyntax, match=err):
        e.run('''
class ABCD:
    pass

''')
    assert 'ABCD' not in e.symbol_table


def test_compare():
    e = Evaluator()
    assert e.run('1 == 2') == (1 == 2)
    assert e.run('3 > 2') == (3 > 2)
    assert e.run('3 >= 2') == (3 >= 2)
    assert e.run('"A" in "America"') == ('A' in 'America')
    assert e.run('"E" not in "America"') == ('E' not in 'America')
    assert e.run('1 is 2') == (1 is 2)  # noqa
    assert e.run('1 is not 2') == (1 is not 2)  # noqa
    assert e.run('3 < 2') == (3 < 2)
    assert e.run('3 <= 2') == (3 <= 2)


def test_continue():
    e = Evaluator()
    e.run('continue')
    assert e.current_interrupt.__class__.__name__ == 'Continue'


def test_delete():
    e = Evaluator()
    e.symbol_table['a'] = 0
    e.symbol_table['b'] = 0
    e.symbol_table['c'] = 0
    e.run('del a, b, c')
    assert 'a' not in e.symbol_table
    assert 'b' not in e.symbol_table
    assert 'c' not in e.symbol_table
    e.symbol_table['l'] = [1, 2, 3, 4]
    e.run('del l[0]')
    assert e.symbol_table['l'] == [2, 3, 4]

    err = 'This delete method is not allowed'
    with pytest.raises(BadSyntax, match=err):
        e.run('del l[2:3]')

    e.symbol_table['dt'] = datetime.now()
    err = 'This delete method is not allowed'
    with pytest.raises(BadSyntax, match=err):
        e.run('del dt.year')


def test_dict():
    e = Evaluator()
    assert e.run('{1: 111, 2: 222}') == {1: 111, 2: 222}
    e.run('a = {1: 111, 2: 222}')
    assert e.symbol_table['a'] == {1: 111, 2: 222}


def test_dictcomp():
    e = Evaluator()
    assert e.run('{k+1: v**2 for k, v in {1: 1, 2: 11, 3: 111}.items()}') == {
        2: 1,
        3: 121,
        4: 12321,
    }
    assert 'k' not in e.symbol_table
    assert 'v' not in e.symbol_table
    e.run('a = {k+1: v**2 for k, v in {1: 1, 2: 11, 3: 111}.items()}')
    assert e.symbol_table['a'] == {
        2: 1,
        3: 121,
        4: 12321,
    }
    assert 'k' not in e.symbol_table
    assert 'v' not in e.symbol_table


def test_ellipsis():
    e = Evaluator()
    assert e.run('...') == Ellipsis


def test_expr():
    e = Evaluator()
    assert e.run('True') is True
    assert e.run('False') is False
    assert e.run('None') is None
    assert e.run('123') == 123
    assert e.run('"abc"') == 'abc'
    assert e.run('[1, 2, 3]') == [1, 2, 3]
    assert e.run('(1, 2, 3, 3)') == (1, 2, 3, 3)
    assert e.run('{1, 2, 3, 3}') == {1, 2, 3}
    assert e.run('{1: 111, 2: 222}') == {1: 111, 2: 222}


def test_extslice():
    e = Evaluator()
    e.symbol_table['obj'] = GetItemSpy()
    e.run('obj[1,2:3,4]')
    es = e.symbol_table['obj'].queue.pop()
    assert isinstance(es, tuple)
    assert len(es) == 3
    assert es[0] == 1
    assert isinstance(es[1], slice)
    assert es[1].start == 2
    assert es[1].stop == 3
    assert es[1].step is None
    assert es[2] == 4


def test_functiondef():
    e = Evaluator()
    err = 'Defining new function via def syntax is not allowed'
    with pytest.raises(BadSyntax, match=err):
        e.run('''
def abc():
    pass

''')
    assert 'abc' not in e.symbol_table


def test_for():
    total = 0
    for x in [1, 2, 3, 4, 5, 6]:
        total = total + x
        if total > 10:
            continue
        total = total * 2
    else:
        total = total + 10000
    e = Evaluator()
    e.run('''
total = 0
for x in [1, 2, 3, 4, 5, 6]:
    total = total + x
    if total > 10:
        continue
    total = total * 2
else:
    total = total + 10000
''')
    assert e.symbol_table['total'] == total

    total2 = 0
    for x in [1, 2, 3, 4, 5, 6]:
        total2 = total2 + x
        if total2 > 10:
            break
        total2 = total2 * 2
    else:
        total2 = total2 + 10000

    e.run('''
total2 = 0
for x in [1, 2, 3, 4, 5, 6]:
    total2 = total2 + x
    if total2 > 10:
        break
    total2 = total2 * 2
else:
    total2 = total2 + 10000
''')
    assert e.symbol_table['total2'] == total2


def test_formattedvalue():
    e = Evaluator()
    e.symbol_table['before'] = 123456
    e.run('after = f"change {before} to {before:,}!"')
    assert e.symbol_table['after'] == 'change 123456 to 123,456!'


def test_generator_exp():
    e = Evaluator()
    e.symbol_table['r'] = [1, 2, 3]
    err = 'Defining new generator expression is not allowed'
    with pytest.raises(BadSyntax, match=err):
        e.run('x = (i ** 2 for i in r)')
    assert 'x' not in e.symbol_table


def test_global():
    e = Evaluator()
    err = 'You can not use `global` syntax'
    with pytest.raises(BadSyntax, match=err):
        e.run('global x')


def test_if():
    e = Evaluator()
    e.symbol_table['a'] = 1
    e.run('''
if a == 1:
    a = 2
    b = 3
''')
    assert e.symbol_table['a'] == 2
    assert e.symbol_table['b'] == 3

    e.run('''
if a == 1:
    a = 2
    b = 3
    z = 1
else:
    a = 3
    b = 4
    c = 5
''')
    assert e.symbol_table['a'] == 3
    assert e.symbol_table['b'] == 4
    assert e.symbol_table['c'] == 5
    assert 'z' not in e.symbol_table

    e.run('''
if a == 1:
    a = 2
    b = 3
    z = 1
elif a == 3:
    d = 4
    e = 5
    f = 6
else:
    a = 3
    b = 4
    c = 5
    y = 7
''')
    assert e.symbol_table['a'] == 3
    assert e.symbol_table['b'] == 4
    assert e.symbol_table['c'] == 5
    assert e.symbol_table['d'] == 4
    assert e.symbol_table['e'] == 5
    assert e.symbol_table['f'] == 6
    assert 'y' not in e.symbol_table
    assert 'z' not in e.symbol_table


def test_ifexp():
    e = Evaluator()
    assert e.run('100 if 1 == 1 else 200') == 100
    assert e.run('100 if 1 == 2 else 200') == 200


def test_import():
    e = Evaluator()
    err = 'You can not import anything'
    with pytest.raises(BadSyntax, match=err):
        e.run('import sys')
    assert 'sys' not in e.symbol_table


def test_importfrom():
    e = Evaluator()
    err = 'You can not import anything'
    with pytest.raises(BadSyntax, match=err):
        e.run('from os import path')
    assert 'path' not in e.symbol_table


def test_index():
    e = Evaluator()
    e.symbol_table['obj'] = GetItemSpy()
    e.run('obj[10]')
    index = e.symbol_table['obj'].queue.pop()
    assert index == 10
    e.run('obj["asdf"]')
    index = e.symbol_table['obj'].queue.pop()
    assert index == 'asdf'


def test_lambda():
    e = Evaluator()
    err = 'Defining new function via lambda syntax is not allowed'
    with pytest.raises(BadSyntax, match=err):
        e.run('lambda x: x*2')


def test_list():
    e = Evaluator()
    assert e.run('[1, 2, 3]') == [1, 2, 3]
    e.run('a = [1, 2, 3]')
    assert e.symbol_table['a'] == [1, 2, 3]


def test_listcomp():
    e = Evaluator()
    assert e.run('[x ** 2 for x in [1, 2, 3]]') == [1, 4, 9]
    assert 'x' not in e.symbol_table
    assert e.run('[x ** 2 + y for x in [1, 2, 3] for y in [10, 20, 30]]') == (
        [x ** 2 + y for x in [1, 2, 3] for y in [10, 20, 30]]
    )
    assert 'x' not in e.symbol_table
    assert 'y' not in e.symbol_table
    assert e.run('[y ** 2 for x in [1, 2, 3] for y in [x+1, x+3, x+5]]') == (
        [y ** 2 for x in [1, 2, 3] for y in [x+1, x+3, x+5]]
    )
    assert 'x' not in e.symbol_table
    assert 'y' not in e.symbol_table


def test_nameconstant():
    e = Evaluator()
    assert e.run('True') is True
    assert e.run('False') is False
    assert e.run('None') is None
    e.run('x = True')
    e.run('y = False')
    e.run('z = None')
    assert e.symbol_table['x'] is True
    assert e.symbol_table['y'] is False
    assert e.symbol_table['z'] is None


def test_nonlocal():
    e = Evaluator()
    err = 'You can not use `nonlocal` syntax'
    with pytest.raises(BadSyntax, match=err):
        e.run('nonlocal x')


def test_num():
    e = Evaluator()
    assert e.run('123') == 123
    e.run('a = 123')
    assert e.symbol_table['a'] == 123


def test_pass():
    e = Evaluator()
    e.run('pass')


def test_raise():
    e = Evaluator()
    err = 'You can not use `raise` syntax'
    with pytest.raises(BadSyntax, match=err):
        e.run('raise NameError')


def test_return():
    e = Evaluator()
    err = 'You can not use `return` syntax'
    with pytest.raises(BadSyntax, match=err):
        e.run('return True')


def test_set():
    e = Evaluator()
    assert e.run('{1, 1, 2, 3, 3}') == {1, 2, 3}
    e.run('a = {1, 1, 2, 3, 3}')
    assert e.symbol_table['a'] == {1, 2, 3}


def test_setcomp():
    e = Evaluator()
    assert e.run('{x ** 2 for x in [1, 2, 3, 3]}') == {1, 4, 9}
    assert 'x' not in e.symbol_table
    assert e.run('{x ** 2 + y for x in [1, 2, 3] for y in [10, 20, 30]}') == (
        {x ** 2 + y for x in [1, 2, 3] for y in [10, 20, 30]}
    )
    assert 'x' not in e.symbol_table
    assert 'y' not in e.symbol_table
    assert e.run('{y ** 2 for x in [1, 2, 3] for y in [x+1, x+3, x+5]}') == (
        {y ** 2 for x in [1, 2, 3] for y in [x+1, x+3, x+5]}
    )
    assert 'x' not in e.symbol_table
    assert 'y' not in e.symbol_table


def test_slice():
    e = Evaluator()
    e.symbol_table['obj'] = GetItemSpy()
    e.run('obj[10:20:3]')
    s = e.symbol_table['obj'].queue.pop()
    assert isinstance(s, slice)
    assert s.start == 10
    assert s.stop == 20
    assert s.step == 3


def test_str():
    e = Evaluator()
    assert e.run('"asdf"') == 'asdf'
    e.run('a = "asdf"')
    assert e.symbol_table['a'] == 'asdf'


def test_subscript():
    e = Evaluator()
    assert e.run('[10, 20, 30][0]') == 10
    assert e.run('(100, 200, 300)[0]') == 100
    assert e.run('{"a": 1000, "b": 2000, "c": 3000}["a"]') == 1000
    e.run('a = [10, 20, 30][0]')
    e.run('b = (100, 200, 300)[0]')
    e.run('c = {"a": 1000, "b": 2000, "c": 3000}["a"]')
    assert e.symbol_table['a'] == 10
    assert e.symbol_table['b'] == 100
    assert e.symbol_table['c'] == 1000
    e.symbol_table['l'] = [11, 22, 33]
    assert e.run('l[2]') == 33
    e.run('l[2] = 44')
    assert e.symbol_table['l'] == [11, 22, 44]


def test_try():
    e = Evaluator()
    err = 'You can not use `try` syntax'
    with pytest.raises(BadSyntax, match=err):
        e.run('''
try:
    x = 1
except:
    pass
''')
    assert 'x' not in e.symbol_table


def test_tuple():
    e = Evaluator()
    assert e.run('(1, 1, 2, 3, 3)') == (1, 1, 2, 3, 3)
    e.run('a = (1, 1, 2, 3, 3)')
    assert e.symbol_table['a'] == (1, 1, 2, 3, 3)


def test_unaryop():
    e = Evaluator()
    assert e.run('~100') == ~100
    assert e.run('not 100') == (not 100)
    assert e.run('+100') == +100
    assert e.run('-100') == -100


def test_while():
    total = 0
    i = 1
    while total > 100:
        total += i
        i += i
        if i % 10 == 0:
            i += 1
    else:
        total = total + 10000
    e = Evaluator()
    e.run('''
total = 0
i = 1
while total > 100:
    total += i
    i += i
    if i % 10 == 0:
        i += 1
else:
    total = total + 10000
''')
    assert e.symbol_table['total'] == total

    r = 0
    while True:
        break
    else:
        r += 10

    e.run('''
r = 0
while True:
    break
else:
    r += 10
''')
    assert e.symbol_table['r'] == 0


def test_with():
    e = Evaluator()
    err = 'You can not use `with` syntax'
    with pytest.raises(BadSyntax, match=err):
        e.run('''
with some:
    x = 1
''')
    assert 'x' not in e.symbol_table


def test_yield():
    e = Evaluator()
    err = 'You can not use `yield` syntax'
    with pytest.raises(BadSyntax, match=err):
        e.run('x = yield f()')
    assert 'x' not in e.symbol_table


def test_yield_from():
    e = Evaluator()
    err = 'You can not use `yield from` syntax'
    with pytest.raises(BadSyntax, match=err):
        e.run('x = yield from f()')
    assert 'x' not in e.symbol_table


@pytest.mark.parametrize(
    ('expr, expected_decimal_result, expected_num_result,'
     'expected_decimal_local, expected_num_local'),
    [
        ('1', D('1'), 1, {}, {}),
        ('1+2', D('3'), 3, {}, {}),
        (
            '0.1+0.1+0.1+0.1+0.1+0.1+0.1+0.1+0.1+0.1',
            D('1'),
            0.1+0.1+0.1+0.1+0.1+0.1+0.1+0.1+0.1+0.1,
            {},
            {}
        ),
        ('1-2', D('-1'), -1, {}, {}),
        ('4*5', D('20'), 20, {}, {}),
        ('1/2', D('0.5'), 0.5, {}, {}),
        ('10%3', D('1'), 1, {}, {}),
        ('2**3', D('8'), 8, {}, {}),
        ('(1+2)**3', D('27'), 27, {}, {}),
        ('max(1,2,3,4,5)', D('5'), 5, {}, {}),
        ('math.floor(3.2)', D('3'), 3, {}, {}),
        ('round', round, round, {}, {}),
        ('math', math, math, {}, {}),
        ('1+math.e', D(math.e) + D('1'), math.e + 1, {}, {}),
        ('[1,2,3]', [D('1'), D('2'), D('3')], [1, 2, 3], {}, {}),
        (
            '[x*10 for x in [0,1,2]]',
            [D('0'), D('10'), D('20')],
            [0, 10, 20],
            {},
            {}
        ),
        ('(1,2,3)', (D('1'), D('2'), D('3')), (1, 2, 3), {}, {}),
        ('{3,2,10}', {D('2'), D('3'), D('10')}, {2, 3, 10}, {}, {}),
        ('{x%2 for x in [1,2,3,4]}', {D('0'), D('1')}, {0, 1}, {}, {}),
        ('{"ab": 123}', {'ab': D('123')}, {'ab': 123}, {}, {}),
        (
            '{"k"+str(x): x-1 for x in [1,2,3]}',
            {'k1': D('0'), 'k2': D('1'), 'k3': D('2')},
            {'k1': 0, 'k2': 1, 'k3': 2},
            {},
            {}
        ),
        ('3 in [1,2,3]', True, True, {}, {}),
        ('[1,2,3,12,3].count(3)', 2, 2, {}, {}),
        ('{1,2} & {2,3}', {D('2')}, {2}, {}, {}),
        ('"item4"', 'item4', 'item4', {}, {}),
        ('"{}4".format("item")', 'item4', 'item4', {}, {}),
        ('money = 1000', None, None, {'money': D('1000')}, {'money': 1000}),
        (
            'money = 1000; money * 2',
            D('2000'),
            2000,
            {'money': D('1000')},
            {'money': 1000}
        ),
        (
            'money = 1000; f"{money}원"',
            '1000원',
            '1000원',
            {'money': D('1000')},
            {'money': 1000}
        ),
        (
            'a = 11;\nif a > 10:\n    a += 100\na',
            D('111'),
            111,
            {'a': D(111)},
            {'a': 111}
        ),
    ]
)
def test_calculate_fine(
    expr: str,
    expected_decimal_result,
    expected_num_result,
    expected_decimal_local: dict,
    expected_num_local: dict,
):

    decimal_result, decimal_local = calculate(
        expr, decimal_mode=True)

    num_result, num_local = calculate(expr, decimal_mode=False)

    assert expected_decimal_result == decimal_result
    assert expected_decimal_local.keys() == decimal_local.keys()

    for key in decimal_local.keys():
        expected = expected_decimal_local[key]
        local = decimal_local[key]

        assert type(expected) == type(local)

        if callable(expected):
            assert expected(1) == local(1)
        else:
            assert expected == local

    assert expected_num_result == num_result
    assert expected_num_local.keys() == num_local.keys()

    for key in num_local.keys():
        expected = expected_num_local[key]
        local = num_local[key]

        assert type(expected) == type(local)

        assert expected == local
