{ 推箱子核心逻辑（Pascal 教学） }
unit game;

interface

const
  MaxW = 32;
  MaxH = 32;
  MaxHist = 1024;

type
  THist = record
    px, py: Integer;
    bfx, bfy, btx, bty: Integer;
    isPush: Boolean;
  end;

  TGameState = record
    map: array[1..MaxW, 1..MaxH] of Char;
    width, height: Integer;
    px, py: Integer;
    moves: Integer;
    won: Boolean;
    histN: Integer;
    hist: array[1..MaxHist] of THist;
  end;

procedure FromRows(const rows: array of string; n: Integer; var s: TGameState);
function TryMove(var s: TGameState; dx, dy: Integer): Boolean;
function Undo(var s: TGameState): Boolean;
procedure RenderAscii(const s: TGameState);

implementation

procedure CheckWin(var s: TGameState);
var
  x, y: Integer;
begin
  s.won := True;
  for y := 1 to s.height do
    for x := 1 to s.width do
      if s.map[x, y] = '$' then
      begin
        s.won := False;
        Exit;
      end;
end;

procedure FromRows(const rows: array of string; n: Integer; var s: TGameState);
var
  y, x, lenr: Integer;
  ch: Char;
begin
  FillChar(s, SizeOf(s), 0);
  s.height := n;
  s.width := 0;
  s.px := 1;
  s.py := 1;
  for y := 1 to MaxH do
    for x := 1 to MaxW do
      s.map[x, y] := ' ';

  for y := 0 to n - 1 do
  begin
    lenr := Length(rows[y]);
    if lenr > s.width then
      s.width := lenr;
    for x := 1 to lenr do
    begin
      ch := rows[y][x];
      case ch of
        '#': s.map[x, y + 1] := '#';
        '.': s.map[x, y + 1] := '.';
        '$': s.map[x, y + 1] := '$';
        '*': s.map[x, y + 1] := '*';
        '@':
          begin
            s.map[x, y + 1] := ' ';
            s.px := x;
            s.py := y + 1;
          end;
        '+':
          begin
            s.map[x, y + 1] := '.';
            s.px := x;
            s.py := y + 1;
          end;
      else
        s.map[x, y + 1] := ' ';
      end;
    end;
  end;
end;

function TryMove(var s: TGameState; dx, dy: Integer): Boolean;
var
  nx, ny, bx, by: Integer;
  ch: Char;
begin
  TryMove := False;
  if s.won then
    Exit;
  nx := s.px + dx;
  ny := s.py + dy;
  if (nx < 1) or (ny < 1) or (nx > s.width) or (ny > s.height) then
    Exit;
  ch := s.map[nx, ny];
  if ch = '#' then
    Exit;

  if (ch = '$') or (ch = '*') then
  begin
    bx := nx + dx;
    by := ny + dy;
    if (bx < 1) or (by < 1) or (bx > s.width) or (by > s.height) then
      Exit;
    ch := s.map[bx, by];
    if (ch = '#') or (ch = '$') or (ch = '*') then
      Exit;
    if s.histN >= MaxHist then
      Exit;
    Inc(s.histN);
    s.hist[s.histN].px := s.px;
    s.hist[s.histN].py := s.py;
    s.hist[s.histN].bfx := nx;
    s.hist[s.histN].bfy := ny;
    s.hist[s.histN].btx := bx;
    s.hist[s.histN].bty := by;
    s.hist[s.histN].isPush := True;
    if s.map[nx, ny] = '*' then
      s.map[nx, ny] := '.'
    else
      s.map[nx, ny] := ' ';
    if s.map[bx, by] = '.' then
      s.map[bx, by] := '*'
    else
      s.map[bx, by] := '$';
    s.px := nx;
    s.py := ny;
    Inc(s.moves);
    CheckWin(s);
    TryMove := True;
    Exit;
  end;

  if s.histN >= MaxHist then
    Exit;
  Inc(s.histN);
  s.hist[s.histN].px := s.px;
  s.hist[s.histN].py := s.py;
  s.hist[s.histN].isPush := False;
  s.px := nx;
  s.py := ny;
  TryMove := True;
end;

function Undo(var s: TGameState): Boolean;
var
  h: THist;
  nx, ny, bx, by: Integer;
begin
  Undo := False;
  if s.won or (s.histN = 0) then
    Exit;
  while s.histN > 0 do
  begin
    h := s.hist[s.histN];
    Dec(s.histN);
    if h.isPush then
    begin
      s.px := h.px;
      s.py := h.py;
      nx := h.bfx;
      ny := h.bfy;
      bx := h.btx;
      by := h.bty;
      if s.map[bx, by] = '*' then
        s.map[bx, by] := '.'
      else
        s.map[bx, by] := ' ';
      if s.map[nx, ny] = '.' then
        s.map[nx, ny] := '*'
      else
        s.map[nx, ny] := '$';
      if s.moves > 0 then
        Dec(s.moves);
      s.won := False;
      Undo := True;
      Exit;
    end
    else
    begin
      s.px := h.px;
      s.py := h.py;
    end;
  end;
  Undo := True;
end;

procedure RenderAscii(const s: TGameState);
var
  x, y: Integer;
  line: string;
  ch: Char;
begin
  for y := 1 to s.height do
  begin
    line := '';
    for x := 1 to s.width do
    begin
      if (x = s.px) and (y = s.py) then
      begin
        if s.map[x, y] = '.' then
          ch := '+'
        else
          ch := '@';
      end
      else
        ch := s.map[x, y];
      line := line + ch;
    end;
    WriteLn(line);
  end;
end;

end.
