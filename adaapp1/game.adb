-- 推箱子核心逻辑（Ada 教学）
with Ada.Strings.Fixed;

package body Game is

   procedure Check_Win (S : in out Game_State) is
   begin
      S.Won := True;
      for Y in 1 .. S.Height loop
         for X in 1 .. S.Width loop
            if S.Map (X, Y) = '$' then
               S.Won := False;
               return;
            end if;
         end loop;
      end loop;
   end Check_Win;

   procedure From_Rows
     (Rows : String_Array; N : Natural; S : out Game_State)
   is
      Len : Natural;
      Ch  : Character;
      R   : String (1 .. 64);
   begin
      S.Map    := (others => (others => ' '));
      S.Width  := 0;
      S.Height := N;
      S.PX     := 1;
      S.PY     := 1;
      S.Moves  := 0;
      S.Won    := False;
      S.Hist_N := 0;
      for Y in 1 .. N loop
         R   := Rows (Y);
         Len := Ada.Strings.Fixed.Trim (R, Ada.Strings.Right)'Length;
         if Len > S.Width then
            S.Width := Len;
         end if;
         for X in 1 .. Len loop
            Ch := R (X);
            case Ch is
               when '#' =>
                  S.Map (X, Y) := '#';
               when '.' =>
                  S.Map (X, Y) := '.';
               when '$' =>
                  S.Map (X, Y) := '$';
               when '*' =>
                  S.Map (X, Y) := '*';
               when '@' =>
                  S.Map (X, Y) := ' ';
                  S.PX         := X;
                  S.PY         := Y;
               when '+' =>
                  S.Map (X, Y) := '.';
                  S.PX         := X;
                  S.PY         := Y;
               when others =>
                  S.Map (X, Y) := ' ';
            end case;
         end loop;
      end loop;
   end From_Rows;

   function Try_Move
     (S : in out Game_State; DX, DY : Integer) return Boolean
   is
      NX, NY, BX, BY : Integer;
      Ch             : Character;
   begin
      if S.Won then
         return False;
      end if;
      NX := S.PX + DX;
      NY := S.PY + DY;
      if NX < 1 or NY < 1 or NX > S.Width or NY > S.Height then
         return False;
      end if;
      Ch := S.Map (NX, NY);
      if Ch = '#' then
         return False;
      end if;
      if Ch = '$' or Ch = '*' then
         BX := NX + DX;
         BY := NY + DY;
         if BX < 1 or BY < 1 or BX > S.Width or BY > S.Height then
            return False;
         end if;
         Ch := S.Map (BX, BY);
         if Ch = '#' or Ch = '$' or Ch = '*' then
            return False;
         end if;
         if S.Hist_N >= Max_Hist then
            return False;
         end if;
         S.Hist_N              := S.Hist_N + 1;
         S.Hist (S.Hist_N)     :=
           (S.PX, S.PY, NX, NY, BX, BY, True);
         if S.Map (NX, NY) = '*' then
            S.Map (NX, NY) := '.';
         else
            S.Map (NX, NY) := ' ';
         end if;
         if S.Map (BX, BY) = '.' then
            S.Map (BX, BY) := '*';
         else
            S.Map (BX, BY) := '$';
         end if;
         S.PX    := NX;
         S.PY    := NY;
         S.Moves := S.Moves + 1;
         Check_Win (S);
         return True;
      end if;
      if S.Hist_N >= Max_Hist then
         return False;
      end if;
      S.Hist_N          := S.Hist_N + 1;
      S.Hist (S.Hist_N) := (S.PX, S.PY, 0, 0, 0, 0, False);
      S.PX              := NX;
      S.PY              := NY;
      return True;
   end Try_Move;

   function Undo (S : in out Game_State) return Boolean is
      H              : Hist_Entry;
      NX, NY, BX, BY : Integer;
   begin
      if S.Won or S.Hist_N = 0 then
         return False;
      end if;
      while S.Hist_N > 0 loop
         H         := S.Hist (S.Hist_N);
         S.Hist_N  := S.Hist_N - 1;
         if H.Is_Push then
            S.PX := H.PX;
            S.PY := H.PY;
            NX   := H.BFX;
            NY   := H.BFY;
            BX   := H.BTX;
            BY   := H.BTY;
            if S.Map (BX, BY) = '*' then
               S.Map (BX, BY) := '.';
            else
               S.Map (BX, BY) := ' ';
            end if;
            if S.Map (NX, NY) = '.' then
               S.Map (NX, NY) := '*';
            else
               S.Map (NX, NY) := '$';
            end if;
            if S.Moves > 0 then
               S.Moves := S.Moves - 1;
            end if;
            S.Won := False;
            return True;
         else
            S.PX := H.PX;
            S.PY := H.PY;
         end if;
      end loop;
      return True;
   end Undo;

   procedure Render_Ascii (S : Game_State) is
      Ch : Character;
   begin
      for Y in 1 .. S.Height loop
         for X in 1 .. S.Width loop
            if X = S.PX and Y = S.PY then
               if S.Map (X, Y) = '.' then
                  Ch := '+';
               else
                  Ch := '@';
               end if;
            else
               Ch := S.Map (X, Y);
            end if;
            Ada.Text_IO.Put (Ch);
         end loop;
         Ada.Text_IO.New_Line;
      end loop;
   end Render_Ascii;

end Game;
