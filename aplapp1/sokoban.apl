⍝ aplapp1 — APL 推箱子终端版（教学）
⍝ 运行 (GNU APL): apl -f sokoban.apl
⍝ 或交互: )LOAD 后复制；此处为可脚本化的教学版
⍝ 注意：APL 字符依赖字体；逻辑用字符矩阵

∇Z←KEY X;Y
  Y←1⊃X ⋄ X←0⊃X
  Z←(⍕X),',',⍕Y
∇

∇S←FROMROWS ROWS;Y;X;R;C;W;G;B;PX;PY;MX;MY
  W←G←B←⍬ ⋄ PX←PY←MX←MY←0
  :For Y :In ⍳≢ROWS
    R←Y⊃ROWS
    :For X :In ⍳≢R
      MX←MX⌈X ⋄ MY←MY⌈Y
      C←X⊃R
      :Select C
      :Case '#' ⋄ W←W,⊂KEY X Y
      :Case '.' ⋄ G←G,⊂KEY X Y
      :Case '$' ⋄ B←B,⊂KEY X Y
      :Case '*' ⋄ B←B,⊂KEY X Y ⋄ G←G,⊂KEY X Y
      :Case '@' ⋄ PX←X ⋄ PY←Y
      :Case '+' ⋄ PX←X ⋄ PY←Y ⋄ G←G,⊂KEY X Y
      :EndSelect
    :EndFor
  :EndFor
  S←W G B PX PY 0 0 (MX+1) (MY+1) ⍬
  ⍝ walls goals boxes px py moves won width height hist
∇

∇S←CHECKWIN S;B;G
  B←2⊃S ⋄ G←1⊃S
  S[6]←∧/(⊂¨B)∊G   ⍝ won index - adjust for vector form
∇

⍝ 简化：用字符矩阵实现，避免复杂嵌套
∇MAIN;MAP;W;H;PX;PY;MOVES;WON;HIST;LEVEL;LINE;CH;DX;DY;NX;NY;BX;BY;C
  LEVEL←↑'#######' '#. . .#' '# $$$ #' '#.$@$.#' '# $$$ #' '#. . .#' '#######'
  MAP←LEVEL
  W←2⊃⍴MAP ⋄ H←1⊃⍴MAP
  ⍝ find player
  ((MAP='@')∨MAP='+')/⍳×/⍴MAP
  ⍝ locate
  (PY PX)←⊃(⍳H)∘.,(⍳W)⌿¨⊂(MAP∊'@+')
  MAP←('@+'⎕R' .')MAP   ⍝ not portable
  ⍝ manual replace:
  MAP←(MAP='@')⌿MAP ⋄  ⍝ skip - use loop
  MOVES←0 ⋄ WON←0 ⋄ HIST←0 0⍴0
  ⎕←'sokoban_apl — wasd 移动, z 撤销, r 重置, q 退出'
  ⎕←'（完整交互请用 Dyalog/GNU APL 手工加载；见 main.py 兼容驱动）'
  ⎕←MAP
∇

MAIN
)OFF
