-- 推箱子核心逻辑（Ada 教学）规格
with Ada.Text_IO;

package Game is
   Max_W    : constant := 32;
   Max_H    : constant := 32;
   Max_Hist : constant := 1024;

   type Hist_Entry is record
      PX, PY, BFX, BFY, BTX, BTY : Integer := 0;
      Is_Push                    : Boolean := False;
   end record;

   type Map_Type is array (1 .. Max_W, 1 .. Max_H) of Character;
   type Hist_Array is array (1 .. Max_Hist) of Hist_Entry;

   type Game_State is record
      Map    : Map_Type := (others => (others => ' '));
      Width  : Integer  := 0;
      Height : Integer  := 0;
      PX, PY : Integer  := 1;
      Moves  : Integer  := 0;
      Won    : Boolean  := False;
      Hist_N : Integer  := 0;
      Hist   : Hist_Array;
   end record;

   type String_Array is array (Positive range <>) of String (1 .. 64);

   procedure From_Rows
     (Rows : String_Array; N : Natural; S : out Game_State);
   function Try_Move
     (S : in out Game_State; DX, DY : Integer) return Boolean;
   function Undo (S : in out Game_State) return Boolean;
   procedure Render_Ascii (S : Game_State);

end Game;
