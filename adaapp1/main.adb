-- adaapp1 — Ada 推箱子终端版（教学）
-- 编译: gnatmake main.adb
with Ada.Text_IO; use Ada.Text_IO;
with Ada.Strings.Fixed;
with Game;        use Game;

procedure Main is
   Level : String_Array (1 .. 7);
   State : Game_State;
   Line  : String (1 .. 80);
   Last  : Natural;
   Ch    : Character;
   Ok    : Boolean;
   Flag  : String (1 .. 8);

   procedure Pad (Dst : out String; Src : String) is
   begin
      Dst := (others => ' ');
      Dst (1 .. Src'Length) := Src;
   end Pad;

   procedure Init is
   begin
      Pad (Level (1), "#######");
      Pad (Level (2), "#. . .#");
      Pad (Level (3), "# $$$ #");
      Pad (Level (4), "#.$@$.#");
      Pad (Level (5), "# $$$ #");
      Pad (Level (6), "#. . .#");
      Pad (Level (7), "#######");
      From_Rows (Level, 7, State);
   end Init;

begin
   Init;
   Put_Line ("sokoban_ada — wasd 移动, z 撤销, r 重置, q 退出");
   loop
      New_Line;
      Render_Ascii (State);
      if State.Won then
         Flag := " WIN!   ";
      else
         Flag := "        ";
      end if;
      Put_Line
        ("moves=" & Integer'Image (State.Moves) &
         Ada.Strings.Fixed.Trim (Flag, Ada.Strings.Right));
      Put ("> ");
      exit when End_Of_File;
      Get_Line (Line, Last);
      if Last = 0 then
         goto Continue;
      end if;
      Ch := Line (1);
      if Ch in 'A' .. 'Z' then
         Ch := Character'Val (Character'Pos (Ch) + 32);
      end if;
      case Ch is
         when 'w' =>
            Ok := Try_Move (State, 0, -1);
         when 's' =>
            Ok := Try_Move (State, 0, 1);
         when 'a' =>
            Ok := Try_Move (State, -1, 0);
         when 'd' =>
            Ok := Try_Move (State, 1, 0);
         when 'z' =>
            Ok := Undo (State);
         when 'r' =>
            Init;
         when 'q' =>
            exit;
         when others =>
            null;
      end case;
      if State.Won then
         Put_Line ("Level clear!");
      end if;
      <<Continue>>
   end loop;
end Main;
