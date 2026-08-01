package com.whj.sokoban;

/**
 * 关卡数据（教学演示子集，由 levels.json 导出）。
 * J2ME 常用做法：把资源编译进 class，避免运行时 JSON 解析库。
 */
public final class LevelsData {
    private LevelsData() {}

    public static final int COUNT = 35;

    public static String name(int index) {
        return NAMES[index];
    }

    public static String[] puzzle(int index) {
        return PUZZLES[index];
    }

    public static String solution(int index) {
        return SOLUTIONS[index];
    }

    public static boolean hasSolution(int index) {
        String s = SOLUTIONS[index];
        return s != null && s.length() > 0;
    }

    private static final String[] NAMES = {
        "Classic 1",
        "Classic 2",
        "Classic 3",
        "Classic 4",
        "Classic 5",
        "Classic 6",
        "Classic 7",
        "Classic 8",
        "Classic 9",
        "Classic 10",
        "Classic 11",
        "Classic 12",
        "Classic 12X",
        "Classic 13",
        "Classic 14",
        "Madeleine",
        "Meredith Angelo",
        "Heather",
        "Wendy",
        "Beatrice",
        "Veronica",
        "Penelope",
        "Sophie",
        "Marcea",
        "Zoe",
        "Kelly",
        "Felicity",
        "Carla",
        "Katherine",
        "Fiona",
        "Tracy",
        "Teresa",
        "Abigail",
        "Mandy",
        "Isabelle"
    };

    private static final String[][] PUZZLES = {
        { // 0 Classic 1
            "##############",
            "#..--#-----###",
            "#..--#-$--$--#",
            "#..--#$####--#",
            "#..----@-##--#",
            "#..--#-#--$-##",
            "######-##$-$-#",
            "--#-$--$-$-$-#",
            "--#----#-----#",
            "--############"
        },
        { // 1 Classic 2
            "--------#########",
            "--------#-----@##",
            "--------#-$#$-###",
            "--------#-$--$###",
            "--------##$-$-###",
            "#########-$-#-###",
            "#....--##-$--$--#",
            "##...----$--$---#",
            "#....--##########",
            "#################"
        },
        { // 2 Classic 3
            "-----------########",
            "-----------#--....#",
            "############--....#",
            "#----#--$-$---....#",
            "#-$$$#$--$-#--....#",
            "#--$-----$-#--....#",
            "#-$$-#$-$-$########",
            "#--$-#-----########",
            "##-################",
            "#----#----#########",
            "#-----$---#########",
            "#--$$#$$--@########",
            "#----#----#########",
            "###################"
        },
        { // 3 Classic 4
            "--------#########",
            "--------#---#####",
            "--------#-#$##--#",
            "--------#-----$-#",
            "#########-###---#",
            "#....--##-$--$###",
            "#....----$-$$-###",
            "#....--##$--$-@##",
            "#########--$--###",
            "--------#-$-$--##",
            "--------###-##-##",
            "----------#----##",
            "----------#######"
        },
        { // 4 Classic 5
            "######--####",
            "#..--#-##@##",
            "#..--###---#",
            "#..-----$$-#",
            "#..--#-#-$-#",
            "#..###-#-$-#",
            "####-$-#$--#",
            "---#--$#-$-#",
            "---#-$--$--#",
            "---#--##---#",
            "---#########"
        },
        { // 5 Classic 6
            "-------######",
            "-#######---##",
            "##-#-@##-$$-#",
            "#----$------#",
            "#--$--###---#",
            "###-#####$###",
            "#-$--###-..##",
            "#-$-$-$-...##",
            "#----###...##",
            "#-$$-#-#...##",
            "#--###-######",
            "#############"
        },
        { // 6 Classic 7
            "--##############",
            "--#--###########",
            "--#----$---$-$-#",
            "--#-$#-$-#--$--#",
            "--#--$-$--#----#",
            "###-$#-#--####-#",
            "#@#$-$-$--##---#",
            "#----$-#$#---#-#",
            "#---$----$-$-$-#",
            "#####--#########",
            "--#------#######",
            "--#------#######",
            "--#......#######",
            "--#......#######",
            "--#......#######",
            "--##############"
        },
        { // 7 Classic 8
            "----------#######",
            "----------#--...#",
            "------#####--...#",
            "------#------.-.#",
            "------#--##--...#",
            "------##-##--...#",
            "-----###-########",
            "-----#-$$$-######",
            "-#####--$-$-#####",
            "##---#$-$---#---#",
            "#@-$--$----$--$-#",
            "######-$$-$-#####",
            "-----#------#####",
            "-----############"
        },
        { // 8 Classic 9
            "-###--#############",
            "##@####-------#---#",
            "#-$$---$$--$-$-...#",
            "#--$$$#----$--#...#",
            "#-$---#-$$-$$-#...#",
            "###---#--$----#...#",
            "#-----#-$-$-$-#...#",
            "#----######-###...#",
            "##-#--#--$-$--#...#",
            "#--##-#-$$-$-$##..#",
            "#-..#-#--$------#.#",
            "#-..#-#-$$$-$$$-#.#",
            "#####-#-------#-#.#",
            "----#-#########-#.#",
            "----#-----------#.#",
            "----###############"
        },
        { // 9 Classic 10
            "----------#########",
            "-----####-#--######",
            "---###-@###$-######",
            "--##------$--######",
            "-##--$-$$##-#######",
            "-#--#$##-----######",
            "-#-#-$-$$-#-#######",
            "-#---$-#--#-$-#####",
            "####----#--$$-#---#",
            "####-##-$---------#",
            "#.----###--########",
            "#..-..#-###########",
            "#...#.#############",
            "#.....#############",
            "###################"
        },
        { // 10 Classic 11
            "#################",
            "#--------------##",
            "#-#-######-----##",
            "#-#--$-$-$-$#--##",
            "#-#---$@$---##-##",
            "#-#-#$-$-$###...#",
            "#-#---$-$--##...#",
            "#-###$$$-$-##...#",
            "#-----#-##-##...#",
            "#####---##-##...#",
            "----#####-----###",
            "--------#-----###",
            "--------#########"
        },
        { // 11 Classic 12
            "#################",
            "#--------------##",
            "#-#-######-----##",
            "#-#--$-$-$-$#--##",
            "#-#---$@$---##-##",
            "#-#--$-$-$###...#",
            "#-#---$-$--##...#",
            "#-###$$$-$-##...#",
            "#-----#-##-##...#",
            "#####---##-##...#",
            "----#####-----###",
            "--------#-----###",
            "--------#########"
        },
        { // 12 Classic 12X
            "---################",
            "--##---##--########",
            "###-----#--#----###",
            "#--$-#$-#--#--...-#",
            "#-#-$#@$##-#-#.#.-#",
            "#--#-#$--#----.-.-#",
            "#-$----$-#-#-#.#.-#",
            "#---##--##$-$-.-.-#",
            "#-$-#---#--#$#.#.-#",
            "##-$--$---$--$...-#",
            "-#$-######----##--#",
            "-#--#----##########",
            "-##################"
        },
        { // 13 Classic 13
            "-------###########",
            "-#######-----#####",
            "-#-----#-$@$-#####",
            "-#$$-#---#########",
            "-#-###......##---#",
            "-#---$......##-#-#",
            "-#-###......-----#",
            "##---####-###-#$##",
            "#--#$---#--$--#-##",
            "#--$-$$$--#-$##-##",
            "#---$-$-###$$-#-##",
            "#####-----$---#-##",
            "----###-###---#-##",
            "------#-----#---##",
            "------########--##",
            "-------------#####"
        },
        { // 14 Classic 14
            "---##############",
            "---#---#--#######",
            "---#--$---#######",
            "-###-#$---#######",
            "-#--$--##$---####",
            "-#--#-@-$-#-$####",
            "-#--#------$-####",
            "-##-####$##-----#",
            "-#-$#.....#-#---#",
            "-#--$..**.-$#-###",
            "##--#.....#---###",
            "#---###-#########",
            "#-$$--#--########",
            "#--#-----########",
            "######---########",
            "-----############"
        },
        { // 15 Madeleine
            "########",
            "##--.--#",
            "#-#$@$-#",
            "#-$.-*$#",
            "#--*.$-#",
            "#-.-#$.#",
            "#-#.---#",
            "########"
        },
        { // 16 Meredith Angelo
            "########",
            "#.-.$--#",
            "#.$$$*-#",
            "#--*-#-#",
            "#*$.-#-#",
            "#.-$*--#",
            "#-$.+--#",
            "########"
        },
        { // 17 Heather
            "########",
            "#-#-.-.#",
            "#-$-#--#",
            "#.-$#-$#",
            "#-$@*.-#",
            "#-#$--.#",
            "#--$.###",
            "########"
        },
        { // 18 Wendy
            "########",
            "#---.-.#",
            "#@$#$--#",
            "#-.$-$-#",
            "#-$-#--#",
            "##*$#-##",
            "##...-##",
            "########"
        },
        { // 19 Beatrice
            "#######",
            "#----.#",
            "#@#-$-#",
            "#*--$##",
            "#-----#",
            "#$$##.#",
            "#.-*.-#",
            "#.--$-#",
            "#######"
        },
        { // 20 Veronica
            "########",
            "#----#-#",
            "#.#-$*-#",
            "#$$-*-@#",
            "#.-.$.##",
            "#--#$.##",
            "##-----#",
            "########"
        },
        { // 21 Penelope
            "########",
            "#-$.-.-#",
            "#.$.$--#",
            "#---*.$#",
            "#-$#-$.#",
            "#-$+$-.#",
            "########"
        },
        { // 22 Sophie
            "########",
            "##@-..-#",
            "#-#$#.-#",
            "#---..*#",
            "##$$-$-#",
            "#--$-$-#",
            "#---#-.#",
            "########"
        },
        { // 23 Marcea
            "########",
            "#@$.-$.#",
            "#--$-$.#",
            "#-$$-$-#",
            "#.-$.#*#",
            "###$*.-#",
            "#-.-.-.#",
            "########"
        },
        { // 24 Zoe
            "########",
            "##-##--#",
            "#-$@$$-#",
            "#.#----#",
            "#.#$##-#",
            "#---$.-#",
            "#-*.--.#",
            "########"
        },
        { // 25 Kelly
            "########",
            "##---#-#",
            "#--$$-.#",
            "#-$@$###",
            "#.#$---#",
            "#.*-##-#",
            "#.--.--#",
            "########"
        },
        { // 26 Felicity
            "########",
            "#-$.-..#",
            "#.$.$$-#",
            "#--.$--#",
            "###--###",
            "#..*-$-#",
            "#$$*$--#",
            "#@*--.##",
            "########"
        },
        { // 27 Carla
            "########",
            "#-#@---#",
            "#.-**-##",
            "#.-#---#",
            "#-$$-#.#",
            "#-$-**-#",
            "#--.$--#",
            "########"
        },
        { // 28 Katherine
            "########",
            "#.--.-##",
            "#-#--$-#",
            "#$*$##@#",
            "#--$.#-#",
            "#.-#-$-#",
            "##--.--#",
            "########"
        },
        { // 29 Fiona
            "########",
            "#--..#-#",
            "#-$--$-#",
            "#*$#$--#",
            "#-@$.*##",
            "#-#.---#",
            "#--.-###",
            "########"
        },
        { // 30 Tracy
            "##########",
            "#-..-$---#",
            "#$.-.-$--#",
            "#.-####*-#",
            "#$$-$--$*#",
            "#+*----.-#",
            "##########"
        },
        { // 31 Teresa
            "#######",
            "#+$--.#",
            "#*$*$-#",
            "#-$--.#",
            "#.$*$-#",
            "#.--.-#",
            "#######"
        },
        { // 32 Abigail
            "########",
            "#---.$-#",
            "#$@*-#.#",
            "#-**$--#",
            "#--$.$$#",
            "#.#.-#.#",
            "#-$---.#",
            "########"
        },
        { // 33 Mandy
            "########",
            "#@$.---#",
            "#$*$--.#",
            "#.$-*#.#",
            "#--$-$-#",
            "#-#$..##",
            "#..-$--#",
            "########"
        },
        { // 34 Isabelle
            "#######",
            "###.###",
            "#-.-###",
            "#.$*$.#",
            "#..--.#",
            "#*#$$$#",
            "#--@$.#",
            "##$$--#",
            "#-----#",
            "#######"
        }
    };

    private static final String[] SOLUTIONS = {
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "urrdDDuuulldddLuruurrdddLruuLrddlUlldRurruulllDurrrddllUdrruulDlddlddrrrUULrULuurDllluRdrddrddllluuUddlluuRlddrrdrrruulLruulDrdrddlllulluurRRurrDDlUllllddrrdrrUdrUdlllulluurDurruulDrdrruuLrddlDDrdLLruuuruulDrdD",
        "llldduuurdrduldluuurdrddudludlddl",
        "RdrruUluurDldDrdLurUdlllUlldRRllddrRlluurrRRuuullDDldRuuurrddrDuluurDlddLLrrrUdlllulldddrrUULrrruuulldDldRuuurrrDulllddllDurruurrdddLLrrrUdlllulluRdrdrruuullDldldRRddllUUruururrrDldddLruuuulldlddrRlluurDldRllddrrUUluulDDrrdrrUrUdldlluluururrdDuulldlddrddllUUruurDldlddrrurrUUddlldlluuruururrrDulllddldlddrrurruuUruLdddrUUddldllURlluurDldR",
        "urrrrdrddlUruulllllddrRRRdrUUdllllluurDurrrDrddlddllUUddrruuruulullldlddRUluurrrrdrddlUlLDlluuurrrrDullllddRRlluurrrrdrddlddlllUdrrruuruulullllddrrdDuulluurDlddRddRuluUluurrrrdrddlULLDDulluuurrrrDullllddRluurDDDuuurrrdrddlUlUdrruLdlLdlDuUrrruuLLrDrdLLdlluuuRRllddRluurDDDuRRurrddlUruLuLLrDrdLLdlluuuRR",
        "urrdddrrddlLdlluRUUlDurrrrdddLuruulluuulldDuurrrrdLulllddRdrrUUddlluluurrRddLruulDrddlldlUdrdRldlUruurrrdddlLLrrruLruuluulDrdrdddllluuulURddddrruruulLUlldRurruulllDurrrddlldddRRdrUllluulUdrddlUruurrdLulDurruulDrddllDldRRluurruulDrdLulDDldRuuulDurruullDurrdddllD",
        "ldddllluuruuulldDRdrUdlddrrruuLruLdrddllluuuluurrrDulllddrdRRUrDllluluurrrDDrdLuuulllddrdddrrUUUdddlluuuRldddrruuLulDrrruLdlluluurrrDulllddrdrrddrUlulluluurrrdDLrrDLuuulllddRluurrrdddddllUdrrrUluuLrdddllulUURlddrdrruuurDlddlluluurDRRddllUluRddrruuuuulllDDrRlluurrrdDllddlUUrrruulDrdDLLrruulDldddrrUU",
        "rruuuldrdrdrlluuddrrrrlllluurdrurdlldluuddrrrruulldluurr",
        "rrrddlddRUrDuUddllLdlluRRRuullDurrddldlluRuurrdrruLuurDldLddLrurrUdlldldlluRuRRllddrUruurrdLuuurDlddrdLLruuurDlddlLdlluRuuRRDrUllldRlddrUluurrrruulllDurrrddlddrUluUruLddddLruuurDlddlLdlluRuuRuuRlddRDrUllldRlddrUluurrrruuLrddlddrUlulllddrRUruUddldlluRuRlddrUrUdlluRdrrdLLullddrUUluR",
        "rrrdruuldudlllldlrlrdrruuddduuullddruulldrlruddddrdrrrrrddddddr",
        "rrrrddrdllrllrrdluddlrllduluddlrrlrlllddd",
        "ddrruduurllulddrdrlulddddlddldld",
        "ururruluuurrrrdddlurrrldluurduuddlllurddruuuudddrduuddlllurdddrluullluuull",
        "rrddrdddlLUlLdlUUdrrrdrruuullDurrdddllLulUdrdrrruuulldLdlldRurururuulDLLrrrdrdddllLuurUdldlldRurururrdddllUllluRdrrdrruuullDuruulldlDDldRuuururrddldLruruulldldDrruruLddlllddrUluRddRRlluuuuRurrddldLrurrdddLruuuluulDlldDlddrUUrrUrrdddlLUUddrruuuluulldlDDuururrdLrdrdddlluuUdlllddrUluRddRRuuurrdddLruuulldLrdLururrddLruulldlddlluRluRddrRULrrruullDuruulDDrrddlLdllluuruuRurrddlDuruulldlddRluururrddrdddLLLUdrruruuluulldlddlddRluuruururrddrddlLrruullDuruulldlddlddrUUddRRUrruullDurrdddLLruruuluulldlDururrddrdddllUUddLrurruuluulldldDuurRurDlllddlddRluuruurrDDuullddlddrUUddRRUrrdLulUUddrruuLuulldlDDlddrUdrRuLrrruuluulldRDrrddlldllluRdrrurruulluurDldDuulldDlddrUdrrUrrdLulUUddLdlluRUddrRuuLrdrruuLrddllLrrrdLuruuluulldRDDlddlluuRlddrruRldlluRdrRuuurrdddLLuuuuurDlddddrruuuLrdddlluuUruulldlDDlddrUUddRRuuurrdddLruuuluulldlDururDDDurrdddlLrruuulullldDlddrUUddRRUULrdLurUrrdddLruuullddRdrUllldlluRluRddrRurrdLLuuuruulldlDDRluururrddlDuruLddlllddrUluRuuRlddddRluuuururrddldLruruulDlldDlddrUUrrUdllddrRlluurruruulldlDDrruruLddlllddrrrUrrdLLuUUdlllddrURlluRdrRuurrDulldLdrdLrrrUdlluuuruulDDDldlluRuuRurrddldLdlUrruruulDrdrDululllDDrrUruLddlddrrrUdllUlullddRluurrdrUUdllldRR",
        "lddldrdluurldruuldluuurlludrdrl",
        "uuddrdruurllluududldrrrlldludrrrlududrldudrldlrd",
        "ruudrluluulllddlllurlrrdrrrdldlludrllldruudrrrrrullllllllllrurrr",
        "rrrddrrrdldullrdllulurdddurluldrdlrllurruldudlur",
        "drrullldrrdrrdlldddurrllrudrrruuudduudlruddllrurrdlluuruddllurrddl",
        "rddrdrrlddddlullluruuddrurrldrlrlllurrllrdurrrdrdulruuurdddlluruulddrlr",
        "uuuurddllurdurrudrrullddruuuurdurlrlddldddululuuudrdruudrldrudduulluuuulduuullluuul"
    };
}
