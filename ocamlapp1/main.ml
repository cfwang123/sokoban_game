(* ocamlapp1 — OCaml 推箱子终端版（教学）
   编译: ocamlc -o sokoban game.ml main.ml
   或: ocamlopt -o sokoban game.ml main.ml *)

let level = [
  "#######";
  "#. . .#";
  "# $$$ #";
  "#.$@$.#";
  "# $$$ #";
  "#. . .#";
  "#######";
]

let () =
  let state = ref (Game.from_rows level) in
  print_endline "sokoban_ocaml — wasd 移动, z 撤销, r 重置, q 退出";
  let rec loop () =
    print_newline ();
    print_string (Game.render_ascii !state);
    let flag = if !state.Game.won then " WIN!" else "" in
    Printf.printf "moves=%d%s\n> %!" !state.Game.moves flag;
    match try Some (input_line stdin) with End_of_file -> None with
    | None -> ()
    | Some line ->
      let line = String.trim line in
      if line = "" then loop ()
      else
        let ch = Char.lowercase_ascii line.[0] in
        begin match ch with
        | 'w' -> state := Game.try_move !state 0 (-1)
        | 's' -> state := Game.try_move !state 0 1
        | 'a' -> state := Game.try_move !state (-1) 0
        | 'd' -> state := Game.try_move !state 1 0
        | 'z' -> state := Game.undo !state
        | 'r' -> state := Game.from_rows level
        | 'q' -> raise Exit
        | _ -> ()
        end;
        if !state.Game.won then print_endline "Level clear!";
        loop ()
  in
  try loop () with Exit -> ()
