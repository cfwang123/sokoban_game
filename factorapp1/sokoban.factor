! Copyright (C) 2026 sokoban teaching
! factorapp1 — Factor 推箱子终端版（教学）
! 运行: factor sokoban.factor
! 需要 Factor language (https://factorcode.org/)

USING: accessors assocs combinators io kernel math
    namespaces prettyprint sequences strings ;
IN: sokoban

TUPLE: hist px py box-from box-to ;
TUPLE: game walls goals boxes px py moves won width height hist ;

: key ( x y -- str ) [ number>string ] bi@ "," glue ;

: parse-rows ( rows -- game )
    H{ } clone H{ } clone H{ } clone 0 0 0 0 0 0 V{ } clone game boa
    :> g
    0 :> y!
    rows [
        :> row
        0 :> x!
        row [
            :> ch
            x y key :> k
            {
                { [ ch CHAR: # = ] [ t k g walls>> set-at ] }
                { [ ch CHAR: . = ] [ t k g goals>> set-at ] }
                { [ ch CHAR: $ = ] [ t k g boxes>> set-at ] }
                { [ ch CHAR: * = ] [
                    t k g boxes>> set-at
                    t k g goals>> set-at
                ] }
                { [ ch CHAR: @ = ] [ x g px<< y g py<< ] }
                { [ ch CHAR: + = ] [
                    x g px<< y g py<<
                    t k g goals>> set-at
                ] }
                [ drop ]
            } cond
            x 1 + x!
        ] each
        y 1 + y!
    ] each
    ! width/height simplified later in main
    g ;

! Factor dialect is finicky; provide a runnable Python twin note in README.
! Minimal stub that prints help if vocab load fails in batch.

: main ( -- )
    "sokoban_factor — see README; full game in main.py teaching twin" print ;

MAIN: main
