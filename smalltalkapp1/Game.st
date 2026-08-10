"推箱子核心逻辑（GNU Smalltalk 教学）"

Object subclass: GameState [
    | walls goals boxes px py moves won width height hist |

    GameState class >> fromRows: rows [
        | s maxX maxY |
        s := self new.
        s initEmpty.
        maxX := 0. maxY := 0.
        rows keysAndValuesDo: [ :yi :row |
            | y |
            y := yi - 1.
            maxY := y.
            1 to: row size do: [ :xi |
                | x ch k |
                x := xi - 1.
                (x > maxX) ifTrue: [ maxX := x ].
                ch := row at: xi.
                k := s keyX: x y: y.
                (ch = $#) ifTrue: [ s walls add: k ].
                (ch = $.) ifTrue: [ s goals add: k ].
                (ch = $$) ifTrue: [ s boxes add: k ].
                (ch = $*) ifTrue: [ s boxes add: k. s goals add: k ].
                (ch = $@) ifTrue: [ s px: x. s py: y ].
                (ch = $+) ifTrue: [ s px: x. s py: y. s goals add: k ].
            ].
        ].
        s width: maxX + 1.
        s height: maxY + 1.
        ^s
    ]

    initEmpty [
        walls := Set new.
        goals := Set new.
        boxes := Set new.
        px := 0. py := 0. moves := 0. won := false.
        width := 0. height := 0.
        hist := OrderedCollection new.
    ]

    keyX: x y: y [ ^x printString , ',' , y printString ]

    walls [ ^walls ]
    goals [ ^goals ]
    boxes [ ^boxes ]
    px [ ^px ] px: v [ px := v ]
    py [ ^py ] py: v [ py := v ]
    moves [ ^moves ]
    won [ ^won ]
    width [ ^width ] width: v [ width := v ]
    height [ ^height ] height: v [ height := v ]

    checkWin [
        won := boxes allSatisfy: [ :b | goals includes: b ]
    ]

    tryMoveDx: dx dy: dy [
        | nx ny nk bx by bk |
        won ifTrue: [ ^false ].
        nx := px + dx. ny := py + dy.
        nk := self keyX: nx y: ny.
        (walls includes: nk) ifTrue: [ ^false ].
        (boxes includes: nk) ifTrue: [
            bx := nx + dx. by := ny + dy.
            bk := self keyX: bx y: by.
            ((walls includes: bk) or: [ boxes includes: bk ]) ifTrue: [ ^false ].
            hist add: { px. py. nk. bk }.
            boxes remove: nk.
            boxes add: bk.
            px := nx. py := ny.
            moves := moves + 1.
            self checkWin.
            ^true
        ].
        hist add: { px. py. nil. nil }.
        px := nx. py := ny.
        ^true
    ]

    undo [
        | e |
        (won or: [ hist isEmpty ]) ifTrue: [ ^false ].
        [ hist isEmpty ] whileFalse: [
            e := hist removeLast.
            (e at: 3) isNil ifFalse: [
                px := e at: 1. py := e at: 2.
                boxes remove: (e at: 4) ifAbsent: [].
                boxes add: (e at: 3).
                (moves > 0) ifTrue: [ moves := moves - 1 ].
                won := false.
                ^true
            ].
            px := e at: 1. py := e at: 2.
        ].
        ^true
    ]

    renderAscii [
        | out |
        out := WriteStream on: String new.
        0 to: height - 1 do: [ :y |
            0 to: width - 1 do: [ :x |
                | k |
                k := self keyX: x y: y.
                ((px = x) and: [ py = y ]) ifTrue: [
                    out nextPut: ((goals includes: k) ifTrue: [ $+ ] ifFalse: [ $@ ])
                ] ifFalse: [
                    (boxes includes: k) ifTrue: [
                        out nextPut: ((goals includes: k) ifTrue: [ $* ] ifFalse: [ $$ ])
                    ] ifFalse: [
                        (walls includes: k) ifTrue: [ out nextPut: $# ]
                        ifFalse: [
                            (goals includes: k) ifTrue: [ out nextPut: $. ]
                            ifFalse: [ out nextPut: $  ]
                        ]
                    ]
                ]
            ].
            out nl
        ].
        ^out contents
    ]
]
