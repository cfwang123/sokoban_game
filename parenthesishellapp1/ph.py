#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Parenthesis Hell interpreter (Python).

Spec: https://esolangs.org/wiki/Parenthesis_Hell
Wire format / eval aligned with qpliu/esolang Haskell interpreter.

Values: Nil | Cons(a, b)
Encoding (Show/Read):
  show Nil              = "()"
  show (Cons a b)       = "(" + shows(a) + ")"  where
    shows Nil           = ""
    shows (Cons a b)    = "(" + shows(a) + ")" + shows(b)
  equivalently top-level readNext after '(':
    ')'     -> Nil
    '(' car cdr -> Cons (no extra close between car/cdr)

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
from typing import Callable, Dict, List, Optional, Tuple, Union


@dataclass(frozen=True)
class NilType:
    pass


NIL = NilType()


@dataclass(frozen=True)
class Cons:
    car: "Value"
    cdr: "Value"


Value = Union[NilType, Cons]
Scope = Dict[object, object]
PhFunc = Callable[[Value, Scope, Value], object]


class PhError(Exception):
    pass


def is_nil(v: Value) -> bool:
    return isinstance(v, NilType)


def vcar(v: Value) -> Value:
    return v.car if isinstance(v, Cons) else NIL


def vcdr(v: Value) -> Value:
    return v.cdr if isinstance(v, Cons) else NIL


# ----- Parse / print --------------------------------------------------------


def parse(src: str) -> Value:
    chars = [c for c in src if c in "()"]
    i = 0
    n = len(chars)

    def parse_inner() -> Value:
        nonlocal i
        if i >= n:
            raise PhError("unmatched '('")
        if chars[i] == ")":
            i += 1
            return NIL
        if chars[i] != "(":
            raise PhError("expected '('")
        i += 1  # '('
        a = parse_inner()
        d = parse_inner()
        return Cons(a, d)

    def parse_top() -> Value:
        nonlocal i
        if i >= n:
            return NIL
        if chars[i] != "(":
            raise PhError("expected '(' at start")
        i += 1
        return parse_inner()

    # skip to first (
    while i < n and chars[i] != "(":
        i += 1
    if i >= n:
        return NIL
    return parse_top()


def value_to_source(v: Value) -> str:
    def shows(x: Value) -> str:
        if is_nil(x):
            return ""
        assert isinstance(x, Cons)
        return "(" + shows(x.car) + ")" + shows(x.cdr)

    return "(" + shows(v) + ")"


# ----- ASCII string encoding (Value.hs) -------------------------------------


def str_to_value(s: str) -> Value:
    if s == "":
        return Cons(NIL, NIL)

    def encode_from(idx: int) -> Value:
        if idx >= len(s):
            return Cons(NIL, NIL)
        ch = s[idx]
        o = ord(ch)

        def bits(b: int) -> Value:
            if b < 0:
                return encode_from(idx + 1)
            nested = bits(b - 1)
            if (o >> b) & 1:
                return Cons(nested, NIL)
            return Cons(NIL, nested)

        return bits(7)

    return encode_from(0)


def value_to_str(v: Value) -> str:
    out: List[str] = []

    def take_bits(rest: Value, b: int, byte: int) -> Optional[Value]:
        if b < 0:
            out.append(chr(byte & 255))
            return rest
        if is_nil(rest) or not isinstance(rest, Cons):
            return None
        if is_nil(rest.car):
            return take_bits(rest.cdr, b - 1, byte)
        # bit set: Cons(nested, Nil)
        return take_bits(rest.car, b - 1, byte | (1 << b))

    cur: Optional[Value] = v
    while cur is not None and not is_nil(cur):
        nxt = take_bits(cur, 7, 0)
        if nxt is None:
            break
        cur = nxt
    return "".join(out)


# ----- Eval (trampoline) ----------------------------------------------------


class _Thunk:
    __slots__ = ("fn",)

    def __init__(self, fn: Callable[[], object]):
        self.fn = fn


def force(x: object) -> Value:
    while isinstance(x, _Thunk):
        x = x.fn()
    assert isinstance(x, (NilType, Cons))
    return x


def _lookup(scope: Scope, name: Value) -> Optional[PhFunc]:
    cur: Optional[Scope] = scope
    while cur is not None:
        if name in cur:
            return cur[name]  # type: ignore
        outer = cur.get("__outer__")
        if not isinstance(outer, dict):
            break
        cur = outer
    return None


def eval_raw(expr: Value, scope: Scope, inp: Value) -> object:
    if is_nil(expr):
        return inp
    assert isinstance(expr, Cons)
    fn = _lookup(scope, expr.car)
    if fn is None:
        raise PhError(f"undefined function {value_to_source(expr.car)}")
    return fn(expr.cdr, scope, inp)


def make_root() -> Scope:
    def f_quote(arg: Value, scope: Scope, inp: Value) -> Value:
        return arg

    def f_car(arg: Value, scope: Scope, inp: Value) -> Value:
        return vcar(force(eval_raw(arg, scope, inp)))

    def f_cdr(arg: Value, scope: Scope, inp: Value) -> Value:
        return vcdr(force(eval_raw(arg, scope, inp)))

    def f_cons(arg: Value, scope: Scope, inp: Value) -> Value:
        if is_nil(arg):
            return NIL
        assert isinstance(arg, Cons)
        h = force(eval_raw(arg.car, scope, inp))
        t = force(eval_raw(arg.cdr, scope, inp))
        return Cons(h, t)

    def f_if(arg: Value, scope: Scope, inp: Value) -> object:
        if is_nil(arg) or is_nil(vcdr(arg)):
            return NIL
        assert isinstance(arg, Cons)
        cond = force(eval_raw(arg.car, scope, inp))
        body = arg.cdr
        assert isinstance(body, Cons)
        if not is_nil(cond):
            return _Thunk(lambda: eval_raw(body.car, scope, inp))
        return _Thunk(lambda: eval_raw(body.cdr, scope, inp))

    def f_eval(arg: Value, scope: Scope, inp: Value) -> object:
        e = force(eval_raw(arg, scope, inp))
        return _Thunk(lambda: eval_raw(e, scope, inp))

    def f_let(arg: Value, scope: Scope, inp: Value) -> object:
        if is_nil(arg):
            return NIL
        assert isinstance(arg, Cons)
        bindings = arg.car
        body = arg.cdr
        new_scope: Scope = {"__outer__": scope}

        def make_user(fn_body: Value) -> PhFunc:
            def user(uarg: Value, uscope: Scope, uinp: Value) -> object:
                evaluated = force(eval_raw(uarg, uscope, uinp))
                return _Thunk(lambda: eval_raw(fn_body, new_scope, evaluated))

            return user

        b = bindings
        while not is_nil(b):
            assert isinstance(b, Cons)
            item = b.car
            b = b.cdr
            if is_nil(item) or not isinstance(item, Cons):
                continue
            new_scope[item.car] = make_user(item.cdr)

        return _Thunk(lambda: eval_raw(body, new_scope, inp))

    return {
        NIL: f_quote,
        Cons(NIL, NIL): f_let,
        Cons(Cons(NIL, NIL), NIL): f_car,
        Cons(NIL, Cons(NIL, NIL)): f_cdr,
        Cons(Cons(NIL, NIL), Cons(NIL, NIL)): f_cons,
        Cons(NIL, Cons(NIL, Cons(NIL, NIL))): f_if,
        Cons(Cons(Cons(NIL, NIL), NIL), NIL): f_eval,
    }


def ph_eval(expr: Value, inp: Value = NIL) -> Value:
    return force(eval_raw(expr, make_root(), inp))


def run_source(src: str, input_str: Optional[str] = None) -> str:
    prog = parse(src)
    if input_str is None:
        inp: Value = NIL
    elif input_str == "":
        inp = Cons(NIL, NIL)  # empty string
    else:
        inp = str_to_value(input_str)
    return value_to_str(ph_eval(prog, inp))


# ----- Program builders -----------------------------------------------------

Q = NIL
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


def binds(*pairs: Tuple[Value, Value]) -> Value:
    acc: Value = NIL
    for name, body in reversed(pairs):
        acc = Cons(Cons(name, body), acc)
    return acc


def list_from(*xs: Value) -> Value:
    acc: Value = NIL
    for x in reversed(xs):
        acc = Cons(x, acc)
    return acc
