# from pathlib import Path; import sys; sys.path.append(str(Path(__file__).resolve().parent))

from types import EllipsisType
from typing import Callable
import unicodedata

from parsec import anyof, const, literal, many, many1, parse_eof, pchain, pjoin, pmap, pselect, pvoid, satisfy, sepby1, with_default

type ElementLeft = str | EllipsisType
type ElementRight = tuple[str | None, int, bool] | EllipsisType
type Expression = tuple[list[ElementLeft], list[ElementRight]]

is_0_to_9: Callable[[str], bool] = lambda c: c.isdigit()
is_1_to_9: Callable[[str], bool] = lambda c: c.isdigit() and c != '0'
is_identifier_char: Callable[[str], bool] = lambda c: unicodedata.category(c)[0] == 'L' or c == '_'
is_identifier_digit_char: Callable[[str], bool] = lambda c: is_0_to_9(c) or is_identifier_char(c)
is_space: Callable[[str], bool] = lambda c: c.isspace()

parse_0_to_9 = satisfy(is_0_to_9, 'digit 0-9')
parse_1_to_9 = satisfy(is_1_to_9, 'digit 1-9')
parse_integer = pmap(int, pjoin(pchain(parse_1_to_9, pjoin(many(parse_0_to_9)))))

parse_identifier_char = satisfy(is_identifier_char, 'identifier')
parse_identifier_digit_char = satisfy(is_identifier_digit_char, 'identifier or digit')
parse_identifier_left = pjoin(many1(parse_identifier_digit_char))
parse_identifier_right = anyof(
    pjoin(many1(parse_identifier_char)),
    pselect(0, pchain(pvoid(literal('{')), parse_identifier_left, pvoid(literal('}')))),
)

parse_space = satisfy(is_space, 'space')
parse_spaces = many1(parse_space)
parse_spaces_optional = pvoid(many(parse_space))

parse_right_arrow = pvoid(literal('->'))
parse_ellipsis = pmap(const(...), literal('...', desc='ellipsis'))
parse_asterisk = pmap(const(True), literal('*'))

parse_identifier_right_optional = with_default(parse_identifier_right, default=None)
parse_integer_optional = with_default(parse_integer, default=1)
parse_asterisk_optional = with_default(parse_asterisk, default=False)

parse_element_left = anyof(parse_identifier_left, parse_ellipsis)
parse_element_right = anyof(
    pchain(parse_identifier_right_optional, parse_integer, parse_asterisk_optional),
    pchain(parse_identifier_right, parse_integer_optional, parse_asterisk_optional),
    pchain(parse_identifier_right_optional, parse_integer_optional, parse_asterisk),
    parse_ellipsis,
)
parse_elements_left = sepby1(parse_element_left, parse_spaces)
parse_elements_right = sepby1(parse_element_right, parse_spaces)
parse_expression = pchain(
    parse_spaces_optional,
    parse_elements_left,
    parse_spaces_optional,
    parse_right_arrow,
    parse_spaces_optional,
    parse_elements_right,
    parse_spaces_optional,
    parse_eof,
)

# print(pchain(literal('123 '), parse_element_left)('123 .a..', 0))
# print(parse_element_left('a', 0))
# print(parse_element_left('...', 0))
# print(parse_element_right('...', 0))
print(parse_expression(r'a b -> {a3b} {a1}', 0))
print(parse_expression(r'a ... b3 -> {b3k23}2 ... a1', 0))
print(parse_expression('a ... b -> b ... a1', 0))
# print(parse_expression('a ... b -> b ... a1', 0))
# print(parse_identifier_right('aaa', 0))
