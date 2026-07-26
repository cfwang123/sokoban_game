cmake_minimum_required(VERSION 3.11)

project(sokoban C)

set(SOURCES
    src/main.c
    src/gfx.c
    src/font.c
    src/game.c
    src/levels_data.c
)

add_executable(${PROJECT_NAME} ${SOURCES})

target_include_directories(${PROJECT_NAME} PRIVATE include)

target_compile_options(${PROJECT_NAME} PRIVATE -O2 -G0 -Wall)

target_link_libraries(${PROJECT_NAME} PRIVATE
    pspgu
    pspge
    pspdisplay
    pspctrl
    pspvfpu
    m
)

if(PSP)
    create_pbp_file(
        TARGET ${PROJECT_NAME}
        ICON_PATH NULL
        BACKGROUND_PATH NULL
        PREVIEW_PATH NULL
        TITLE "Sokoban"
        VERSION 01.00
    )
endif()
