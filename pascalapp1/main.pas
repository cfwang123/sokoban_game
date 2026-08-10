{ pascalapp1 — Pascal 推箱子终端版（教学）
  编译: fpc main.pas
  运行: ./main  或 main.exe }
program main;

uses
  SysUtils, game;

var
  state: TGameState;
  level: array[0..6] of string;
  line: string;
  ch: Char;
  flag: string;

begin
  level[0] := '#######';
  level[1] := '#. . .#';
  level[2] := '# $$$ #';
  level[3] := '#.$@$.#';
  level[4] := '# $$$ #';
  level[5] := '#. . .#';
  level[6] := '#######';

  FromRows(level, 7, state);
  WriteLn('sokoban_pascal — wasd 移动, z 撤销, r 重置, q 退出');

  while True do
  begin
    WriteLn;
    RenderAscii(state);
    if state.won then
      flag := ' WIN!'
    else
      flag := '';
    WriteLn('moves=', state.moves, flag);
    Write('> ');
    if EOF then
      Break;
    ReadLn(line);
    line := Trim(line);
    if line = '' then
      Continue;
    ch := UpCase(line[1]);
    { 统一小写比较：UpCase 后转回判断 }
    case ch of
      'W': TryMove(state, 0, -1);
      'S': TryMove(state, 0, 1);
      'A': TryMove(state, -1, 0);
      'D': TryMove(state, 1, 0);
      'Z': Undo(state);
      'R': FromRows(level, 7, state);
      'Q': Break;
    end;
    if state.won then
      WriteLn('Level clear!');
  end;
end.
