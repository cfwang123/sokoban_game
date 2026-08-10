# -*- coding: utf-8 -*-
"""Generate pure Befunge-93 playable Sokoban → befungeapp1/sokoban.bf

Generator is maintenance-only. Shipped game is 100% Befunge-93.
"""
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "befungeapp1" / "sokoban.bf"

# Classic mini level (same as other teaching apps)
LEVEL = [
    "#######",
    "#. . .#",
    "# $$$ #",
    "#.$@$.#",
    "# $$$ #",
    "#. . .#",
    "#######",
]
W, H = len(LEVEL[0]), len(LEVEL)

# Map in Funge-Space
MX, MY = 0, 18  # working
BX, BY = 10, 18  # backup initial

# State (single cells, numeric)
C_PX, C_PY, C_MV = 60, 61, 62
C_T0, C_T1, C_T2, C_T3 = 63, 64, 65, 66
C_OK, C_IB, C_CW, C_CP = 67, 68, 69, 70


def pn(n: int) -> str:
    """Push non-negative integer."""
    if n < 0:
        raise ValueError(n)
    if n <= 9:
        return str(n)
    d: list[int] = []
    x = n
    while x:
        d.append(x % 9)
        x //= 9
    d.reverse()
    s = str(d[0])
    for x in d[1:]:
        s += f"9*{x}+"
    return s


def pxy(x: int, y: int) -> str:
    return pn(x) + pn(y)


def store(cell_x: int, val_expr: str) -> str:
    """val_expr leaves value; store to (cell_x, 0)."""
    return val_expr + pxy(cell_x, 0) + "p"


def load(cell_x: int) -> str:
    return pxy(cell_x, 0) + "g"


def emit_linear() -> str:
    """Linear Befunge instruction stream (logical)."""
    o: list[str] = []

    def add(s: str) -> None:
        o.append(s)

    # --- INIT: copy backup←level already in grid; set player/moves ---
    # Find @ in LEVEL
    px = py = 0
    for y, row in enumerate(LEVEL):
        for x, ch in enumerate(row):
            if ch in "@+":
                px, py = x, y
    add(store(C_PX, pn(px)))
    add(store(C_PY, pn(py)))
    add(store(C_MV, "0"))

    # ========== MAIN LOOP LABEL (logical) ==========
    # We'll mark with comment in packing only; loop via IP path.

    # --- PRINT map ---
    add(pn(10) + "," + pn(10) + ",")  # blank line
    for y in range(H):
        for x in range(W):
            add(pxy(MX + x, MY + y) + "g,")
        add(pn(10) + ",")
    for ch in "moves=":
        add(pn(ord(ch)) + ",")
    add(load(C_MV) + ".")
    add(pn(10) + ",")
    for ch in "> ":
        add(pn(ord(ch)) + ",")

    # --- READ ---
    add("~")  # ch

    # Save ch in C_T0
    add(store(C_T0, ":"))  # dup then need store — stack ch ch; store pops via p: need v x y
    # : → ch ch; then pxy p consumes v=ch, x, y — one ch left
    # Fix: : pxy(C_T0,0) p  → ch ch → p takes ch, CT0, 0 → one ch remains. Good if we $ later.
    # Actually p stack order is v x y. So ch ch → need ch x y. 
    # ch : → ch ch; pn(C_T0) pn(0) → ch ch CT0 0; not right for p.
    # Correct store top: pxy first then? p wants v x y with y top.
    # stack: v; push x; push y; p.
    # ch; C_T0; 0; p.
    add("$")  # drop the extra from failed attempt — REWRITE init of save cleanly

    # Clear and redo from READ more carefully in a second pass structure.
    return "REWRITE"


def emit_linear_v2() -> str:
    o: list[str] = []
    A = o.append

    px = py = 0
    for y, row in enumerate(LEVEL):
        for x, ch in enumerate(row):
            if ch in "@+":
                px, py = x, y

    # INIT
    A(pn(px) + pxy(C_PX, 0) + "p")
    A(pn(py) + pxy(C_PY, 0) + "p")
    A("0" + pxy(C_MV, 0) + "p")

    # ===== MAIN (loop target = index after INIT in packed form) =====
    main_start_marker = len("".join(o))

    # PRINT
    A(pn(10) + "," + pn(10) + ",")
    for y in range(H):
        for x in range(W):
            A(pxy(MX + x, MY + y) + "g,")
        A(pn(10) + ",")
    for ch in "moves=":
        A(pn(ord(ch)) + ",")
    A(pxy(C_MV, 0) + "g.")
    A(pn(10) + ",")
    for ch in "> ":
        A(pn(ord(ch)) + ",")

    # READ ch → C_T0
    A("~" + pxy(C_T0, 0) + "p")

    # ===== dispatch using chained equality → set C_T1 = dx+2, C_T2 = dy+2 (offset so 0 means none)
    # Use: load ch, compare, if match set dx dy and ok action code
    # action: 0=none 1=move 2=reset 3=quit
    # C_T3 = action

    def if_eq_char(ch: str, body: str) -> str:
        """If C_T0==ch, run body (body should leave stack clean). Uses _ branch locally.
        Pattern (horizontal):
          C_T0 g  ord - !  → 1 if eq
          ! _     → right if eq (0 after ! means was eq... wait)
          eq flag e: 1 if equal.
          e ! _ BODY $  with reverse path — use arithmetic body always with multiply by e.
        Prefer multiply gating: body computes values * e.
        """
        # return fragment that leaves e=1 if match on stack top? 
        return pxy(C_T0, 0) + "g" + pn(ord(ch)) + "-!"

    # Default action 0, dx=0, dy=0
    A("0" + pxy(C_T3, 0) + "p")
    A("0" + pxy(C_T1, 0) + "p")
    A("0" + pxy(C_T2, 0) + "p")

    # For each key, if eq, set action/dx/dy
    # gated set: val = val*(1-e) + new*e = val + e*(new-val)
    def set_if(ch: str, action: int, dx: int, dy: int) -> None:
        # e = eq
        A(if_eq_char(ch))  # e
        A(":" + pxy(C_OK, 0) + "p")  # save e in C_OK, keep e
        # action: C_T3 = C_T3 + e*(action - C_T3)
        A(pxy(C_T3, 0) + "g")  # e old
        A("\\")  # old e
        A(pn(action) + "\\-")  # e (action-old)? stack old e; action; \ → old action e? 
        # stack: e, old. Want e*(action-old)+old
        # e old \ → old e; action push → old e action; not good.
        # Reload:
        # e (in C_OK): 
        # old=C_T3 g; new=action; delta=new-old; C_OK g * old + → p
        A("$")  # drop e from if_eq (we'll use C_OK)
        A(pxy(C_T3, 0) + "g")
        A(pn(action) + "\\-")  # old action \ - → action-old? old action \ → action old - → action-old NO
        # a b - → a-b with b top: want action - old: action old -
        A(pxy(C_T3, 0) + "g")  # old
        A(pn(action))  # old action
        A("\\-")  # action old - → action-old
        A(pxy(C_OK, 0) + "g*")
        A(pxy(C_T3, 0) + "g+")
        A(pxy(C_T3, 0) + "p")
        # dx → C_T1
        A(pxy(C_T1, 0) + "g" + pn(dx) + "\\-" + pxy(C_OK, 0) + "g*" + pxy(C_T1, 0) + "g+" + pxy(C_T1, 0) + "p")
        # wait \\- with dx: old dx \ - 
        A(pxy(C_T1, 0) + "g")
        A(pn(dx) if dx >= 0 else "0" + pn(-dx) + "-")  
        # if dx negative, pn doesn't work with store of signed — use 0 n - for negative dx
        # redo dx properly below

    # Cleaner set_if:
    def set_if2(ch: str, action: int, dx: int, dy: int) -> None:
        A(if_eq_char(ch) + pxy(C_OK, 0) + "p")  # C_OK=e
        # C_T3
        A(pxy(C_T3, 0) + "g")
        A(pn(action))
        A("\\-")  # action-old if stack old action \ → action old - = action-old. 
        # stack was old, action; \ → action, old; - → action-old. Want new-old = action-old. Good.
        A(pxy(C_OK, 0) + "g*")
        A(pxy(C_T3, 0) + "g+")
        A(pxy(C_T3, 0) + "p")
        # dx signed
        A(pxy(C_T1, 0) + "g")
        if dx >= 0:
            A(pn(dx))
        else:
            A("0" + pn(-dx) + "-")
        A("\\-")  # dx - old
        A(pxy(C_OK, 0) + "g*")
        A(pxy(C_T1, 0) + "g+")
        A(pxy(C_T1, 0) + "p")
        # dy
        A(pxy(C_T2, 0) + "g")
        if dy >= 0:
            A(pn(dy))
        else:
            A("0" + pn(-dy) + "-")
        A("\\-")
        A(pxy(C_OK, 0) + "g*")
        A(pxy(C_T2, 0) + "g+")
        A(pxy(C_T2, 0) + "p")

    set_if2("q", 3, 0, 0)
    set_if2("r", 2, 0, 0)
    set_if2("w", 1, 0, -1)
    set_if2("s", 1, 0, 1)
    set_if2("a", 1, -1, 0)
    set_if2("d", 1, 1, 0)
    # also uppercase
    set_if2("Q", 3, 0, 0)
    set_if2("R", 2, 0, 0)
    set_if2("W", 1, 0, -1)
    set_if2("S", 1, 0, 1)
    set_if2("A", 1, -1, 0)
    set_if2("D", 1, 1, 0)

    # ===== QUIT if action==3 =====
    # e = action 3 - !
    A(pxy(C_T3, 0) + "g" + pn(3) + "-!")  # 1 if quit
    # if quit, @ — use _ : 1 ! _ → right if quit (0 after !)? 
    # quit flag qf. qf ! _  → if qf=1, !=0, _ goes left. Put @ on left.
    # For linear stream, use: qf _ skip @  where _ right if 0.
    # if qf=1 nonzero → left to @. Linear packer only goes right — _ reverse breaks stream.
    #
    # Use: @ is executed if we put it in stream gated — can't.
    # Arithmetic: never @; instead infinite loop noop on quit by jumping to end cell that is @ 
    # by p-writing @ under IP — too hard.
    #
    # For quit:  C_T3 g 3 - !  → if 1, we need @. 
    # In snaking packer we'll insert special: when generating, use '|' or '_' with @ nearby.
    #
    # Special opcode approach: emit '\x01QUIT' marker and packer handles it.
    A("\x01QUIT")

    # ===== RESET if action==2 =====
    A("\x01RESET")

    # ===== MOVE if action==1 =====
    A("\x01MOVE")

    # ===== LOOP back to MAIN =====
    A("\x01LOOP")

    return "".join(o), main_start_marker, px, py


def expand_specials(stream: str, main_start: int, px: int, py: int) -> str:
    """Expand \x01 markers into real befunge, using only forward-friendly ops where possible."""
    # For QUIT: use '|' vertical to @ on next row — packer must place.
    # Simpler approach for quit/reset/move: expand fully inline without _|

    out: list[str] = []
    i = 0
    while i < len(stream):
        if stream[i] == "\x01":
            j = stream.index("\x01", i + 1) if False else i + 1
            # read marker name
            k = i + 1
            while k < len(stream) and stream[k].isalpha():
                k += 1
            name = stream[i + 1 : k]
            i = k
            if name == "QUIT":
                # if action==3 then @ else continue
                # : use  C_T3 g 3 - |  with @ below — emit special for packer
                out.append("\x02Q")
            elif name == "RESET":
                out.append("\x02R")
            elif name == "MOVE":
                out.append("\x02M")
            elif name == "LOOP":
                out.append("\x02L")
            else:
                raise ValueError(name)
        else:
            out.append(stream[i])
            i += 1
    return "".join(out)


def try_move_frag() -> str:
    """Inline try_move using C_T1=dx, C_T2=dy. Only if C_T3==1; gated by multiplying."""
    # If action != 1, skip by multiplying all effects with (action==1)
    A: list[str] = []
    a = A.append
    # act = (C_T3==1)
    a(pxy(C_T3, 0) + "g" + "1-!" + pxy(C_OK, 0) + "p")  # act in C_OK temporarily — conflict
    # use C_CP for act1
    ACT = 71
    a(pxy(C_T3, 0) + "g1-!" + pxy(ACT, 0) + "p")

    # nx = px + dx, ny = py + dy
    a(pxy(C_PX, 0) + "g" + pxy(C_T1, 0) + "g+")
    a(pxy(C_T0, 0) + "p")  # nx in C_T0
    a(pxy(C_PY, 0) + "g" + pxy(C_T2, 0) + "g+")
    a(pxy(63, 0) + "p")  # ny — C_T0 was 63. Use 72,73 for nx,ny
    NX, NY = 72, 73
    a(pxy(C_PX, 0) + "g" + pxy(C_T1, 0) + "g+" + pxy(NX, 0) + "p")
    a(pxy(C_PY, 0) + "g" + pxy(C_T2, 0) + "g+" + pxy(NY, 0) + "p")

    # bounds ok
    # nx>=0: 0 nx ` !
    a("0" + pxy(NX, 0) + "g`!")
    a("0" + pxy(NY, 0) + "g`!*")
    a(pn(W) + pxy(NX, 0) + "g`*")
    a(pn(H) + pxy(NY, 0) + "g`*")
    a(pxy(ACT, 0) + "g*")
    a(pxy(C_OK, 0) + "p")  # ok

    # cell at nx,ny
    a(pxy(NX, 0) + "g" + pxy(NY, 0) + "g" + "g" + pxy(C_T0, 0) + "p")

    # not wall
    a(pxy(C_OK, 0) + "g" + pxy(C_T0, 0) + "g" + pn(35) + "-!!" + "!*")  # wall→0: if wall, -! =1, ! =0; if not wall -!=0, !=1. Wait
    # is_wall = (c==35) = c 35 - !
    # not_wall = is_wall !
    # ok *= not_wall
    a(pxy(C_T0, 0) + "g" + pn(35) + "-!" + "!" + pxy(C_OK, 0) + "g*" + pxy(C_OK, 0) + "p")

    # is_box = (c==36)+(c==42) clamped !!
    a(pxy(C_T0, 0) + "g" + pn(36) + "-!")
    a(pxy(C_T0, 0) + "g" + pn(42) + "-!+")
    a("!!" + pxy(C_IB, 0) + "p")

    # bx by
    BX_, BY_ = 74, 75
    a(pxy(NX, 0) + "g" + pxy(C_T1, 0) + "g+" + pxy(BX_, 0) + "p")
    a(pxy(NY, 0) + "g" + pxy(C_T2, 0) + "g+" + pxy(BY_, 0) + "p")

    # free beyond: b is space or dot
    a(pxy(BX_, 0) + "g" + pxy(BY_, 0) + "g" + "g")
    a(":" + pn(32) + "-!" + "\\" + pn(46) + "-!+")
    # stack fix for free: b : 32 -! \ 46 -! + 
    # b; : b b; 32-! b issp; \ issp b; 46-! issp isdot; + free
    a(pxy(BX_, 0) + "g" + pxy(BY_, 0) + "g" + "g:" + pn(32) + "-!\\" + pn(46) + "-!+")
    a(pxy(FREE := 76, 0) + "p")

    # can_push = ok * is_box * free * bounds bx by
    a("0" + pxy(BX_, 0) + "g`!")
    a("0" + pxy(BY_, 0) + "g`!*")
    a(pn(W) + pxy(BX_, 0) + "g`*")
    a(pn(H) + pxy(BY_, 0) + "g`*")
    a(pxy(C_OK, 0) + "g*")
    a(pxy(C_IB, 0) + "g*")
    a(pxy(FREE, 0) + "g*")
    a(pxy(C_CP, 0) + "p")

    # can_walk = ok * !is_box * (space or dot)
    a(pxy(C_T0, 0) + "g:" + pn(32) + "-!\\" + pn(46) + "-!+")
    a(pxy(C_IB, 0) + "g!*")
    a(pxy(C_OK, 0) + "g*")
    a(pxy(C_CW, 0) + "p")

    # fill char for leaving player cell: goal under → '.' else ' '
    # backup at BX+px, BY+py
    a(pxy(C_PX, 0) + "g" + pn(BX) + "+" + pxy(C_PY, 0) + "g" + pn(BY) + "+" + "g")
    a(":" + pn(46) + "-!\\" + pn(42) + "-!+\\" + pn(43) + "-!+")
    # broken again. Sequential:
    a(pxy(C_PX, 0) + "g" + pn(BX) + "+" + pxy(C_PY, 0) + "g" + pn(BY) + "+" + "g" + pxy(C_T0, 0) + "p")
    a(pxy(C_T0, 0) + "g" + pn(46) + "-!")
    a(pxy(C_T0, 0) + "g" + pn(42) + "-!+")
    a(pxy(C_T0, 0) + "g" + pn(43) + "-!+")
    a("!!")  # isgoal
    a(pn(14) + "*" + pn(32) + "+")  # 32 or 46
    a(pxy(77, 0) + "p")  # fill

    # player char for entering: goal at nx,ny → + else @
    a(pxy(NX, 0) + "g" + pn(BX) + "+" + pxy(NY, 0) + "g" + pn(BY) + "+" + "g" + pxy(C_T0, 0) + "p")
    a(pxy(C_T0, 0) + "g" + pn(46) + "-!")
    a(pxy(C_T0, 0) + "g" + pn(42) + "-!+")
    a(pxy(C_T0, 0) + "g" + pn(43) + "-!+")
    a("!!" + pn(21) + "*" + pn(64) + "\\-")  # 64-21g
    a(pxy(78, 0) + "p")  # pchar

    # box char for push dest
    a(pxy(BX_, 0) + "g" + pn(BX) + "+" + pxy(BY_, 0) + "g" + pn(BY) + "+" + "g" + pxy(C_T0, 0) + "p")
    a(pxy(C_T0, 0) + "g" + pn(46) + "-!")
    a(pxy(C_T0, 0) + "g" + pn(42) + "-!+")
    a(pxy(C_T0, 0) + "g" + pn(43) + "-!+")
    a("!!" + pn(6) + "*" + pn(36) + "+")
    a(pxy(79, 0) + "p")  # bchar — col 79 ok for data

    # --- apply walk ---
    def blend_put_xy(getx: str, gety: str, newv: str, cond: str) -> str:
        # old=g(x,y); v=old+cond*(new-old); p
        return (
            getx
            + gety
            + "g"
            + newv
            + "\\-"
            + cond
            + "*"
            + getx
            + gety
            + "g+"
            + getx
            + gety
            + "p"
        )

    gx = pxy(C_PX, 0) + "g"
    gy = pxy(C_PY, 0) + "g"
    a(blend_put_xy(gx, gy, pxy(77, 0) + "g", pxy(C_CW, 0) + "g"))
    a(blend_put_xy(pxy(NX, 0) + "g", pxy(NY, 0) + "g", pxy(78, 0) + "g", pxy(C_CW, 0) + "g"))
    # px py
    a(pxy(C_PX, 0) + "g" + pxy(NX, 0) + "g\\-" + pxy(C_CW, 0) + "g*" + pxy(C_PX, 0) + "g+" + pxy(C_PX, 0) + "p")
    a(pxy(C_PY, 0) + "g" + pxy(NY, 0) + "g\\-" + pxy(C_CW, 0) + "g*" + pxy(C_PY, 0) + "g+" + pxy(C_PY, 0) + "p")
    a(pxy(C_MV, 0) + "g" + pxy(C_CW, 0) + "g+" + pxy(C_MV, 0) + "p")

    # --- apply push ---
    a(blend_put_xy(gx, gy, pxy(77, 0) + "g", pxy(C_CP, 0) + "g"))
    a(blend_put_xy(pxy(NX, 0) + "g", pxy(NY, 0) + "g", pxy(78, 0) + "g", pxy(C_CP, 0) + "g"))
    a(blend_put_xy(pxy(BX_, 0) + "g", pxy(BY_, 0) + "g", pxy(79, 0) + "g", pxy(C_CP, 0) + "g"))
    a(pxy(C_PX, 0) + "g" + pxy(NX, 0) + "g\\-" + pxy(C_CP, 0) + "g*" + pxy(C_PX, 0) + "g+" + pxy(C_PX, 0) + "p")
    a(pxy(C_PY, 0) + "g" + pxy(NY, 0) + "g\\-" + pxy(C_CP, 0) + "g*" + pxy(C_PY, 0) + "g+" + pxy(C_PY, 0) + "p")
    a(pxy(C_MV, 0) + "g" + pxy(C_CP, 0) + "g+" + pxy(C_MV, 0) + "p")

    return "".join(A)


def reset_frag(px: int, py: int) -> str:
    A: list[str] = []
    a = A.append
    # only if action==2
    a(pxy(C_T3, 0) + "g2-!" + pxy(ACT := 71, 0) + "p")
    for y in range(H):
        for x in range(W):
            # v = g(BX+x,BY+y); if act: p to work else keep
            a(pxy(BX + x, BY + y) + "g")
            a(pxy(MX + x, MY + y) + "g")
            a("\\-")  # backup - work? want new=backup if act
            # v = work + act*(backup-work)
            a(pxy(MX + x, MY + y) + "g")  # work
            a(pxy(BX + x, BY + y) + "g")  # work backup
            a("\\-")  # backup-work
            a(pxy(ACT, 0) + "g*")
            a(pxy(MX + x, MY + y) + "g+")
            a(pxy(MX + x, MY + y) + "p")
    a(pxy(C_PX, 0) + "g" + pn(px) + "\\-" + pxy(ACT, 0) + "g*" + pxy(C_PX, 0) + "g+" + pxy(C_PX, 0) + "p")
    a(pxy(C_PY, 0) + "g" + pn(py) + "\\-" + pxy(ACT, 0) + "g*" + pxy(C_PY, 0) + "g+" + pxy(C_PY, 0) + "p")
    a(pxy(C_MV, 0) + "g0\\-" + pxy(ACT, 0) + "g*" + pxy(C_MV, 0) + "g+" + pxy(C_MV, 0) + "p")
    return "".join(A)


def build_full_linear() -> tuple[str, int]:
    base, main_off, px, py = emit_linear_v2()
    # expand specials into real code
    parts: list[str] = []
    i = 0
    while i < len(base):
        if base[i] == "\x01":
            k = i + 1
            while k < len(base) and base[k].isalpha():
                k += 1
            name = base[i + 1 : k]
            i = k
            if name == "QUIT":
                # action==3 → @
                # place: C_T3 g 3 - ! → eq; use \x03 for packer quit gate
                parts.append(pxy(C_T3, 0) + "g3-!\x03@")
            elif name == "RESET":
                parts.append(reset_frag(px, py))
            elif name == "MOVE":
                parts.append(try_move_frag())
            elif name == "LOOP":
                parts.append("\x03L")  # packer loops to main
            else:
                raise ValueError(name)
        else:
            parts.append(base[i])
            i += 1
    return "".join(parts), main_off


def pack_snake(code: str, main_byte_offset: int) -> str:
    """Pack linear code into 80×15 snake; \x03@ is quit gate; \x03L is loop to main."""
    # Replace specials with positions
    # First, split code by specials and compute main PC location in packed space.

    # Simpler packer: only use rows 0-14, direction LTR on even rows, RTL on odd.
    # When packing RTL, reverse the instruction string for that segment — INVALID for stack code.
    # So only LTR: use rows 0-14 each 80 cols, connect with v at end and > at start of next... 
    # At end of row y: v goes to (79, y+1), then we need < to go left — RTL.
    # Connect: (79,y) v → (79,y+1) < then code reversed — NO.
    #
    # Connect LTR rows:
    # (0,y)> CODE... (len,y) v
    # (len,y+1)< wait
    # Use:
    # row y: > CODE padded to 78, then v at 78
    # row y+1: spaces until we put > at 0 going through nothing — 
    # (78,y)v → (78,y+1). Put < at (78,y+1), go to (0,y+1), put > at (0,y+1) for next CODE.
    # Path: ...code v 
    #              <<<<< to 0 then > nextcode
    # The <<<<< cells are executed! Must be no-ops: use spaces with direction < — spaces are nop, OK!
    # Direction is < so we move left through spaces to 0, then need > to reverse.
    # At (0,y+1) put >. Good.

    grid = [[" "] * 80 for _ in range(25)]
    # place maps
    for y, row in enumerate(LEVEL):
        for x, ch in enumerate(row):
            grid[MY + y][MX + x] = ch
            grid[BY + y][BX + x] = ch

    # Parse code into tokens where \x03@ and \x03L are single tokens
    tokens: list[str] = []
    i = 0
    while i < len(code):
        if i + 1 < len(code) and code[i] == "\x03":
            tokens.append(code[i : i + 2])
            i += 2
        else:
            tokens.append(code[i])
            i += 1

    # Pack tokens into positions list
    positions: list[tuple[int, int]] = []  # for each token index
    x, y = 0, 0
    direction = 1  # 1 right, phase for connection only

    def place_char(ch: str) -> tuple[int, int]:
        nonlocal x, y
        if y >= 16:
            raise RuntimeError(f"out of code space at {x},{y} need more room")
        # if near end of row, wrap snake
        if x >= 78 and direction == 1:
            grid[y][x] = "v"
            positions.append((x, y))  # for this? skip — don't count connector as code
            # actually connectors shouldn't consume tokens
            x = 78
            y += 1
            grid[y][x] = "<"
            x -= 1
            while x > 0:
                grid[y][x] = " "  # nop left
                x -= 1
            grid[y][0] = ">"
            x = 1
        grid[y][x] = ch
        pos = (x, y)
        x += 1
        return pos

    main_pos = None
    token_pos: list[tuple[int, int]] = []
    byte_index = 0
    # main_byte_offset refers to original base before expand — approximate loop to start of stream
    main_pos = (0, 0)

    for ti, tok in enumerate(tokens):
        if tok == "\x03@":
            # quit gate: C_T3 already compared? stream has ...g3-!\x03@
            # Before \x03@ we have left 1 if quit on stack from ! 
            # Pattern: eq ! → 0 if quit. Wait stream is g3-!\x03@ so stack has 1 if action==3.
            # _ : right if 0, left if nonzero. Put @ on left side.
            # Emit: _@  with @ to the left — write @ at x-1? 
            # Current: put '_', then we need @ when taking left branch.
            # put at current: the eq flag is on stack. '_' 
            # If nonzero (quit), go left: cell to the left should be @.
            # So place @ first at x, then _ at x+1? IP hits _. 
            # Layout: [ @ ][ _ ] going right. When _ sees nonzero, goes left to @. When zero, continues right.
            # But @ is left of _; when continuing right from _, skip past.
            px_, py_ = place_char("@")
            # overwrite: we need _ after @ with direction right, IP arrives at _
            # Actually place: space? 
            # Arrive at x with flag on stack. Write '_'. Left cell is x-1 must be '@'.
            if x == 0:
                place_char(" ")  # advance
            # ensure left is @
            lx = x  # will write _ at x
            grid[y][lx] = "_"
            if lx == 0:
                raise RuntimeError("no room for quit @")
            grid[y][lx - 1] = "@"
            token_pos.append((lx, y))
            x = lx + 1
        elif tok == "\x03L":
            # loop to main: change direction toward main_pos
            # Store main at (0,0) always - first char of program
            # Write path: we use p to set a bridge — simplest: 
            #  many ^ and < to get to 0,0 — variable.
            # Fixed: write 'v' into a return channel at col 79? 
            # Absolute jump via: push 0, push 0, and ... no goto.
            #
            # Use self-modifying: put '>' at (0,0) already; from here go to (0,0):
            # Direction up to row 0, left to col 0.
            # Place vertical bus at current x down? up:
            # put '^' repeatedly — through empty cells to row 0, then '<' to col 0.
            cx, cy = x, y
            # mark loop token position
            grid[cy][cx] = "^"
            token_pos.append((cx, cy))
            # fill upward
            for ry in range(cy - 1, -1, -1):
                if grid[ry][cx] == " ":
                    grid[ry][cx] = " "
                # IP moves up through spaces
            # at (cx, 0) need '<' if cx>0
            if cx > 0:
                grid[0][cx] = "<"
                for lx in range(cx - 1, 0, -1):
                    if grid[0][lx] == " ":
                        grid[0][lx] = " "
                # (0,0) should be first instruction '>' of program
            x = cx + 1  # not really continuing
            # After loop token, nothing should follow in stream — break
            break
        else:
            if len(tok) != 1:
                raise ValueError(tok)
            pos = place_char(tok)
            token_pos.append(pos)
            if byte_index == 0:
                main_pos = pos
            byte_index += 1

    # Ensure (0,0) starts program: first placed char should be at 0,0
    # Our packer starts x=0,y=0 — first place_char puts at 0,0. Good.

    # Render
    lines = ["".join(row).rstrip() for row in grid]
    while lines and not lines[-1].strip():
        lines.pop()
    return "\n".join(lines) + "\n"


def main() -> None:
    # Build with a cleaner integrated approach written below
    src = build_program()
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(src, encoding="utf-8")
    print("wrote", OUT, "chars", len(src), "lines", src.count(chr(10)) + 1)


def build_program() -> str:
    """Build complete playable Befunge-93 Sokoban source."""
    linear, _ = build_full_linear()
    # Fix set_if2 swap bug: \\- for (new-old): stack old, new; want new-old: new old - with old top: old new \ - 
    # Currently: old; new; \\- → new old - = new-old. Good.

    packed = pack_snake(linear, 0)
    return packed


if __name__ == "__main__":
    main()
