#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Parenthesis Hell interpreter (Python).

Spec: https://esolangs.org/wiki/Parenthesis_Hell
Reference semantics aligned with qpliu/esolang (Haskell interp):

- Values: Nil | Cons(a, b)
- Program is one expression; evaluated with *input* as the argument
- ()  evaluates to the current input
- Application: (fn . arg) looks up fn in scope and applies to arg (unevaluated cdr);
  each builtin decides how to evaluate arg
- User-defined (letrec): arg is evaluated first; body runs with that value as input

Root functions:
  ()        quote
  (())      letrec
  ((()))    car
  (()())    cdr
  ((())())  cons
  (()()())  if
  (((())))  eval
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Dict, Optional, Tuple, Union


# ----- Values ---------------------------------------------------------------


@dataclass(frozen=True, eq=True)
class NilType:
    def __repr__(self) -> str:
        return "()"


NIL = NilType()


@dataclass(frozen=True, eq=True)
class Cons:
    car: "Value"
    cdr: "Value"

    def __repr__(self) -> str:
        return value_to_source(self)


Value = Union[NilType, Cons]

Scope = Dict[Value, "PhFunc"]
# PhFunc(arg, scope, input, def_scope) -> Value  (may use trampoline thunks)
PhFunc = Callable[[Value, Scope, Value, Scope], Value]


class PhError(Exception):
    pass


def is_nil(v: Value) -> bool:
    return v is NIL or isinstance(v, NilType)


def car(v: Value) -> Value:
    if isinstance(v, Cons):
        return v.car
    return NIL


def cdr(v: Value) -> Value:
    if isinstance(v, Cons):
        return v.cdr
    return NIL


def cons(a: Value, b: Value) -> Value:
    return Cons(a, b)


# ----- Parse / print source -------------------------------------------------


def parse(src: str) -> Value:
    """Parse one Parenthesis Hell value; non-paren chars ignored."""
    i = 0
    n = len(src)

    def skip() -> None:
        nonlocal i
        while i < n and src[i] not in "()":
            i += 1

    def parse_val() -> Value:
        nonlocal i
        skip()
        if i >= n:
            raise PhError("unexpected end of input")
        if src[i] != "(":
            raise PhError(f"expected '(' at {i}")
        i += 1
        skip()
        if i < n and src[i] == ")":
            i += 1
            return NIL
        # Cons: parse car, then cdr (rest of list-shaped nesting per PH reader)
        # PH reader: after '(', either ')' -> Nil, or parse car then parse cdr then
        # In qpliu Read: readNext' ('(':s) = car then cdr both via readNext'
        # Actually: '(' starts cons; first nested value is car, second is cdr.
        # Wait - the Show is: Cons a b => '(' + show a + ')' + show b
        # So source of Cons a b is: ( <source a without outer?> )
        # Looking at Read carefully:
        # readNext ('(':s) = readNext' s
        # readNext' ('(':s) = let (car,s') = readNext' s
        #                     (cdr,s'') = readNext' s'
        #                     (Cons car cdr, s'')
        # readNext' (')':s) = (Nil, s)
        #
        # So inside a paren group started by outer '(', we use readNext' which:
        # - on ')' returns Nil
        # - on '(' parses Cons by reading car and cdr with readNext' (not full readNext)
        #
        # That means the top-level is readNext which requires starting '(',
        # and the inner format is different from show of nested structure...
        #
        # Show Nil = "" (empty between parens of parent) 
        # Show (Cons a b) = '(' + show a + ')' + show b
        # So Cons Nil Nil shown as: (())  because show Nil = "" so '(' + '' + ')' + '' = ()
        # Wait: shows Nil s = s  (empty), shows (Cons a b) s = '(' + shows a (')' + shows b s)
        # Cons Nil Nil: '(' + (shows Nil = '') + ')' + (shows Nil = '') = ()
        # That's just () which is also Nil! Bug?
        #
        # Outer show adds parens: show a = '(' : shows a ")"
        # show Nil = "(" + "" + ")" = "()"
        # show (Cons Nil Nil) = "(" + shows (Cons Nil Nil) + ")"
        #   shows (Cons Nil Nil) = '(' + shows Nil + ')' + shows Nil = '(' + '' + ')' + '' = "()"
        #   full = "(())"
        # Yes (()) is Cons Nil Nil.
        #
        # show (Cons (Cons Nil Nil) Nil) = "(" + "(()" + ")" + "" + ")" 
        #   shows (Cons (Cons Nil Nil) Nil) = '(' + shows(Cons Nil Nil) + ')' + shows Nil
        #   shows(Cons Nil Nil) = "()" 
        #   = "(()" + ")" + "" = "(() )" without space = "(() )"
        #   = "(() )"
        #   full show = "((()))"
        #
        # Reader readNext' on content inside outer parens of a value...
        # Top-level parse uses readNext which needs '('.

        a = parse_inner()
        d = parse_inner()
        skip()
        if i >= n or src[i] != ")":
            raise PhError(f"expected ')' at {i}")
        i += 1
        return Cons(a, d)

    def parse_inner() -> Value:
        """readNext' — used inside an already-opened '('. """
        nonlocal i
        skip()
        if i >= n:
            raise PhError("unmatched '('")
        if src[i] == ")":
            return NIL  # do not consume; caller may be finishing
        if src[i] != "(":
            raise PhError(f"expected '(' or ')' at {i}")
        i += 1  # consume '('
        skip()
        if i < n and src[i] == ")":
            i += 1
            return NIL
        a = parse_inner()
        d = parse_inner()
        skip()
        if i >= n or src[i] != ")":
            raise PhError(f"expected ')' closing cons at {i}")
        i += 1
        return Cons(a, d)

    # Top-level: like readNext
    skip()
    if i >= n:
        return NIL
    if src[i] != "(":
        # ignore junk until '('
        while i < n and src[i] != "(":
            i += 1
        if i >= n:
            return NIL
    result = parse_val()
    return result


def value_to_source(v: Value) -> str:
    """Serialize value matching qpliu Show (with outer parens for whole value)."""

    def shows(x: Value) -> str:
        if is_nil(x):
            return ""
        assert isinstance(x, Cons)
        return "(" + shows(x.car) + ")" + shows(x.cdr)

    return "(" + shows(v) + ")"


# ----- String <-> Value (ASCII, qpliu Value.hs) ------------------------------


def str_to_value(s: str) -> Value:
    if s == "":
        return Cons(NIL, NIL)

    def bits_to_value(bit_indices: list[int], ch: str, rest_fn) -> Value:
        if not bit_indices:
            return rest_fn()
        b = bit_indices[0]
        bs = bit_indices[1:]
        bit_set = (ord(ch) >> b) & 1
        nested = bits_to_value(bs, ch, rest_fn)
        if bit_set:
            return Cons(nested, NIL)
        return Cons(NIL, nested)

    def encode_from(i: int) -> Value:
        if i >= len(s):
            return Cons(NIL, NIL)
        ch = s[i]
        return bits_to_value(list(range(7, -1, -1)), ch, lambda: encode_from(i + 1))

    return encode_from(0)


def value_to_str(v: Value) -> str:
    out: list[str] = []

    def consume(bit_indices: list[int], byte: int, rest: Value) -> Optional[Value]:
        if not bit_indices:
            out.append(chr(byte & 0xFF))
            return rest
        if is_nil(rest):
            return None
        assert isinstance(rest, Cons)
        b = bit_indices[0]
        bs = bit_indices[1:]
        if is_nil(rest.car):
            # bit 0: Cons Nil rest
            return consume(bs, byte, rest.cdr)
        # bit 1: Cons rest' Nil  — bit set
        return consume(bs, byte | (1 << b), rest.car)

    cur: Optional[Value] = v
    while cur is not None and not is_nil(cur):
        nxt = consume(list(range(7, -1, -1)), 0, cur)
        if nxt is None:
            break
        cur = nxt
    return "".join(out)


# ----- Eval -----------------------------------------------------------------


class _Thunk:
    __slots__ = ("fn",)

    def __init__(self, fn: Callable[[], Value]):
        self.fn = fn


def _force(x: Union[Value, _Thunk]) -> Value:
    while isinstance(x, _Thunk):
        x = x.fn()
    return x


def _fn_quote(arg: Value, scope: Scope, inp: Value, def_scope: Scope) -> Value:
    return arg


def _fn_car(arg: Value, scope: Scope, inp: Value, def_scope: Scope) -> Value:
    v = _force(ph_eval_raw(arg, scope, inp))
    return car(v)


def _fn_cdr(arg: Value, scope: Scope, inp: Value, def_scope: Scope) -> Value:
    v = _force(ph_eval_raw(arg, scope, inp))
    return cdr(v)


def _fn_cons(arg: Value, scope: Scope, inp: Value, def_scope: Scope) -> Value:
    if is_nil(arg):
        return NIL
    assert isinstance(arg, Cons)
    h = _force(ph_eval_raw(arg.car, scope, inp))
    t = _force(ph_eval_raw(arg.cdr, scope, inp))
    return Cons(h, t)


def _fn_if(arg: Value, scope: Scope, inp: Value, def_scope: Scope) -> Value:
    if is_nil(arg) or is_nil(cdr(arg)):
        return NIL
    assert isinstance(arg, Cons)
    cond = _force(ph_eval_raw(arg.car, scope, inp))
    body = arg.cdr
    assert isinstance(body, Cons)
    if not is_nil(cond):
        return _Thunk(lambda: ph_eval_raw(body.car, scope, inp))
    return _Thunk(lambda: ph_eval_raw(body.cdr, scope, inp))


def _fn_eval(arg: Value, scope: Scope, inp: Value, def_scope: Scope) -> Value:
    expr = _force(ph_eval_raw(arg, scope, inp))
    return _Thunk(lambda: ph_eval_raw(expr, scope, inp))


def _fn_let(arg: Value, scope: Scope, inp: Value, def_scope: Scope) -> Value:
    if is_nil(arg):
        return NIL
    assert isinstance(arg, Cons)
    bindings = arg.car
    body = arg.cdr

    # Build nested scope
    new_scope: Scope = {}
    new_scope["_outer"] = scope  # type: ignore

    def make_user_fn(fn_body: Value) -> PhFunc:
        def user_fn(uarg: Value, uscope: Scope, uinp: Value, udef: Scope) -> Value:
            # Evaluate argument in caller's scope, then body with result as input
            evaluated = _force(ph_eval_raw(uarg, uscope, uinp))
            return _Thunk(lambda: ph_eval_raw(fn_body, new_scope, evaluated))

        return user_fn

    b = bindings
    while not is_nil(b):
        assert isinstance(b, Cons)
        item = b.car
        b = b.cdr
        if is_nil(item):
            continue
        if not isinstance(item, Cons):
            continue
        name = item.car
        fn_body = item.cdr
        new_scope[name] = make_user_fn(fn_body)

    return _Thunk(lambda: ph_eval_raw(body, new_scope, inp))


def root_scope() -> Scope:
    return {
        NIL: _fn_quote,  # ()
        Cons(NIL, NIL): _fn_let,  # (())
        Cons(Cons(NIL, NIL), NIL): _fn_car,  # ((()))
        Cons(NIL, Cons(NIL, NIL)): _fn_cdr,  # (()())
        Cons(Cons(NIL, NIL), Cons(NIL, NIL)): _fn_cons,  # ((())())
        Cons(NIL, Cons(NIL, Cons(NIL, NIL))): _fn_if,  # (()()())
        Cons(Cons(Cons(NIL, NIL), NIL), NIL): _fn_eval,  # (((())))
    }


def _lookup(scope: Scope, name: Value) -> Optional[PhFunc]:
    cur: Optional[Scope] = scope
    while cur is not None:
        if name in cur and name != "_outer":
            return cur[name]
        outer = cur.get("_outer")  # type: ignore
        if outer is None or not isinstance(outer, dict):
            break
        cur = outer  # type: ignore
    return None


def ph_eval_raw(expr: Value, scope: Scope, inp: Value) -> Union[Value, _Thunk]:
    if is_nil(expr):
        return inp
    assert isinstance(expr, Cons)
    fn_name = expr.car
    arg = expr.cdr
    fn = _lookup(scope, fn_name)
    if fn is None:
        # try root if not nested
        fn = root_scope().get(fn_name)
    if fn is None:
        raise PhError(f"undefined function: {value_to_source(fn_name)}")
    return fn(arg, scope, inp, scope)


def ph_eval(expr: Value, inp: Value = NIL) -> Value:
    """Evaluate expression with input; return fully forced value."""
    return _force(ph_eval_raw(expr, root_scope(), inp))


def ph_eval_source(src: str, input_str: Optional[str] = None) -> Value:
    prog = parse(src)
    inp = str_to_value(input_str) if input_str is not None else NIL
    return ph_eval(prog, inp)


def run_source(src: str, input_str: str = "") -> str:
    """Evaluate program; decode result as ASCII string (like qpliu ph.hs)."""
    prog = parse(src)
    inp = str_to_value(input_str) if input_str != "" else NIL
    # cat with empty input: use Cons(Nil,Nil) as empty string when input_str==""?
    # ph.hs: strToValue input from getContents; empty file -> strToValue [] = Cons Nil Nil
    if input_str == "":
        # For programs that need empty string input vs Nil:
        # Hello world uses Nil input typically (no need for input)
        result = ph_eval(prog, NIL)
    else:
        result = ph_eval(prog, str_to_value(input_str))
    return value_to_str(result)


# ----- Helpers for building programs ----------------------------------------

# Builtin names
Q = NIL  # quote
LET = Cons(NIL, NIL)
CAR = Cons(Cons(NIL, NIL), NIL)
CDR = Cons(NIL, Cons(NIL, NIL))
CONS = Cons(Cons(NIL, NIL), Cons(NIL, NIL))
IF = Cons(NIL, Cons(NIL, Cons(NIL, NIL)))
EV = Cons(Cons(Cons(NIL, NIL), NIL), NIL)


def app(fn: Value, arg: Value) -> Value:
    return Cons(fn, arg)


def q(x: Value) -> Value:
    return app(Q, x)


def ph_car(x: Value) -> Value:
    return app(CAR, x)


def ph_cdr(x: Value) -> Value:
    return app(CDR, x)


def ph_cons(a: Value, d: Value) -> Value:
    return app(CONS, Cons(a, d))


def ph_if(cond: Value, then: Value, else_: Value) -> Value:
    return app(IF, Cons(cond, Cons(then, else_)))


def ph_let(bindings: Value, body: Value) -> Value:
    return app(LET, Cons(bindings, body))


def bind(name: Value, body: Value) -> Value:
    return Cons(name, body)


def bind_list(pairs: list[Tuple[Value, Value]]) -> Value:
    acc: Value = NIL
    for name, body in reversed(pairs):
        acc = Cons(bind(name, body), acc)
    return acc
