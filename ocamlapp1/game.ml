(* 推箱子核心逻辑（OCaml 教学） *)

module S = Set.Make(String)

type hist = {
  px : int; py : int;
  box_from : string option;
  box_to : string option;
}

type state = {
  walls : S.t; goals : S.t; boxes : S.t;
  px : int; py : int;
  moves : int; won : bool;
  width : int; height : int;
  hist : hist list;
}

let key x y = Printf.sprintf "%d,%d" x y

let from_rows rows =
  let walls = ref S.empty and goals = ref S.empty and boxes = ref S.empty in
  let px = ref 0 and py = ref 0 and max_x = ref 0 and max_y = ref 0 in
  List.iteri (fun y row ->
    max_y := y;
    String.iteri (fun x ch ->
      if x > !max_x then max_x := x;
      let k = key x y in
      match ch with
      | '#' -> walls := S.add k !walls
      | '.' -> goals := S.add k !goals
      | '$' -> boxes := S.add k !boxes
      | '*' -> boxes := S.add k !boxes; goals := S.add k !goals
      | '@' -> px := x; py := y
      | '+' -> px := x; py := y; goals := S.add k !goals
      | _ -> ()
    ) row
  ) rows;
  {
    walls = !walls; goals = !goals; boxes = !boxes;
    px = !px; py = !py; moves = 0; won = false;
    width = !max_x + 1; height = !max_y + 1; hist = [];
  }

let check_win boxes goals =
  S.for_all (fun b -> S.mem b goals) boxes

let try_move s dx dy =
  if s.won then s else
  let nx = s.px + dx and ny = s.py + dy in
  let nk = key nx ny in
  if S.mem nk s.walls then s
  else if S.mem nk s.boxes then
    let bx = nx + dx and by = ny + dy in
    let bk = key bx by in
    if S.mem bk s.walls || S.mem bk s.boxes then s
    else
      let boxes = S.add bk (S.remove nk s.boxes) in
      { s with
        boxes; px = nx; py = ny; moves = s.moves + 1;
        won = check_win boxes s.goals;
        hist = { px = s.px; py = s.py; box_from = Some nk; box_to = Some bk } :: s.hist }
  else
    { s with px = nx; py = ny;
      hist = { px = s.px; py = s.py; box_from = None; box_to = None } :: s.hist }

let rec undo s =
  if s.won || s.hist = [] then s
  else
    match s.hist with
    | [] -> s
    | h :: rest ->
      match h.box_from with
      | None ->
          undo { s with px = h.px; py = h.py; hist = rest }
      | Some bf ->
          let bt = Option.value h.box_to ~default:bf in
          let boxes = S.add bf (S.remove bt s.boxes) in
          { s with
            boxes; px = h.px; py = h.py;
            moves = max 0 (s.moves - 1); won = false; hist = rest }

let render_ascii s =
  let buf = Buffer.create 128 in
  for y = 0 to s.height - 1 do
    for x = 0 to s.width - 1 do
      let k = key x y in
      let ch =
        if s.px = x && s.py = y then
          if S.mem k s.goals then '+' else '@'
        else if S.mem k s.boxes then
          if S.mem k s.goals then '*' else '$'
        else if S.mem k s.walls then '#'
        else if S.mem k s.goals then '.'
        else ' '
      in
      Buffer.add_char buf ch
    done;
    Buffer.add_char buf '\n'
  done;
  Buffer.contents buf
