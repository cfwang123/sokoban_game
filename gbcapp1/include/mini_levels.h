/* generated mini levels */
#ifndef MINI_LEVELS_H
#define MINI_LEVELS_H
#define MINI_LEVEL_COUNT 12
typedef struct { const char *name; const char *const *rows; const char *solution; } MiniLevel;
static const char *const ml0_rows[] = {
  "#######",
  "#. . .#",
  "# $$$ #",
  "#.$@$.#",
  "# $$$ #",
  "#. . .#",
  "#######",
  0
};
static const char *const ml1_rows[] = {
  "###",
  "#@#",
  "#$#",
  "#.#",
  "###",
  0
};
static const char *const ml2_rows[] = {
  "#####",
  "#.$@#",
  "#####",
  0
};
static const char *const ml3_rows[] = {
  "###",
  "#.###",
  "#*$-#",
  "#--@#",
  "#####",
  0
};
static const char *const ml4_rows[] = {
  "--#####",
  "###---##",
  "#.*-#@-#",
  "##$###-#",
  "-#-----#",
  "-#######",
  0
};
static const char *const ml5_rows[] = {
  "----#####",
  "--###---#",
  "###.*-#-#",
  "#@$.$#--#",
  "##-----##",
  "-#######",
  0
};
static const char *const ml6_rows[] = {
  "#########",
  "#-------#",
  "#-*..##-#",
  "##$#$#--#",
  "-#-@---##",
  "-#######",
  0
};
static const char *const ml7_rows[] = {
  "#####",
  "#---##",
  "#-.*-#",
  "#--$@#",
  "#--###",
  "####",
  0
};
static const char *const ml8_rows[] = {
  "-######",
  "-#----#",
  "##-$*$#",
  "#@$...#",
  "#######",
  0
};
static const char *const ml9_rows[] = {
  "---#####",
  "---#.$-#",
  "---#.$-#",
  "####.#-#",
  "#@$-*--#",
  "##---###",
  "-#####",
  0
};
static const char *const ml10_rows[] = {
  "######",
  "#----#",
  "#@-*-#",
  "#-*.###",
  "##-$--#",
  "-##---#",
  "--#####",
  0
};
static const char *const ml11_rows[] = {
  "####",
  "#--##",
  "#-$.##",
  "#--*.###",
  "#--**$-#",
  "###---@#",
  "--######",
  0
};
static const MiniLevel g_mini_levels[MINI_LEVEL_COUNT] = {
  { "Classic Star", ml0_rows, "ULrRldDLUdrRluurDlllURdddlUrurrrDLuuurDldlluuRlddrrddLruulluurRddlUdrddlLuurD" },
  { "1 L", ml1_rows, "D" },
  { "1 R", ml2_rows, "L" },
  { "2 L", ml3_rows, "llUdrruL" },
  { "2 R", ml4_rows, "ulldLrurrdrddllllU" },
  { "3 L", ml5_rows, "RdrrrruruulldLrurrddldllU" },
  { "3 R", ml6_rows, "rUdrruruulllllldRurrrrrddldllllU" },
  { "4 L", ml7_rows, "LruLulldRlddrU" },
  { "4 R", ml8_rows, "RRluurDurrD" },
  { "5 L", ml9_rows, "RdrrUrruuuLrdLrddlldlluR" },
  { "7 L", ml10_rows, "urrrdLullddRdRUddrruLdlUluluurD" },
  { "7 R", ml11_rows, "llULdrrruLdlluUlluurDldRldR" }
};
#endif
