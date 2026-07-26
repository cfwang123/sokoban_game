# Classic pspdev Makefile (alternative to CMake)
TARGET = sokoban
OBJS = src/main.o src/gfx.o src/font.o src/game.o src/levels_data.o

INCDIR = include
CFLAGS = -O2 -G0 -Wall
CXXFLAGS = $(CFLAGS) -fno-exceptions -fno-rtti
ASFLAGS = $(CFLAGS)

LIBDIR =
LDFLAGS =
LIBS = -lpspgu -lpspge -lpspdisplay -lpspctrl -lpspvfpu -lm

EXTRA_TARGETS = EBOOT.PBP
PSP_EBOOT_TITLE = Sokoban

PSPSDK = $(shell psp-config --pspsdk-path)
include $(PSPSDK)/lib/build.mak
