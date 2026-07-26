# Sokoban GBA — bare-metal (arm-none-eabi-gcc)
TARGET   := sokoban
BUILD    := build
SRC      := src
INC      := include

# Toolchain: DEVKITARM, ARM_NONE_EABI_PREFIX, common install paths, or PATH
ifneq ($(DEVKITARM),)
  PREFIX := $(DEVKITARM)/bin/arm-none-eabi-
else ifneq ($(ARM_NONE_EABI_PREFIX),)
  PREFIX := $(ARM_NONE_EABI_PREFIX)
else ifneq ($(wildcard /opt/devkitpro/devkitARM/bin/arm-none-eabi-gcc),)
  PREFIX := /opt/devkitpro/devkitARM/bin/arm-none-eabi-
else
  PREFIX := arm-none-eabi-
endif

CC      := $(PREFIX)gcc
AS      := $(PREFIX)gcc
OBJCOPY := $(PREFIX)objcopy
SIZE    := $(PREFIX)size

ARCH    := -mthumb -mthumb-interwork -mcpu=arm7tdmi
CFLAGS  := $(ARCH) -O2 -fomit-frame-pointer -ffast-math \
           -ffreestanding -fno-strict-aliasing \
           -Wall -Wextra -I$(INC)
ASFLAGS := $(ARCH) -ffreestanding
LDFLAGS := $(ARCH) -nostdlib -T gba.ld -Wl,-Map,$(BUILD)/$(TARGET).map

# Explicit list so generated *.c are always linked (wildcard is expand-at-parse-time)
C_SRCS  := $(SRC)/main.c $(SRC)/game.c $(SRC)/gfx.c $(SRC)/sound.c $(SRC)/sys.c \
           $(SRC)/tiles_data.c $(SRC)/levels_data.c
S_SRCS  := $(SRC)/crt0.s
OBJS    := $(patsubst $(SRC)/%.c,$(BUILD)/%.o,$(C_SRCS)) \
           $(patsubst $(SRC)/%.s,$(BUILD)/%.o,$(S_SRCS))

.PHONY: all clean assets run

all: assets $(TARGET).gba

assets: $(SRC)/tiles_data.c $(SRC)/levels_data.c

$(SRC)/tiles_data.c: tools/gen_tiles.py
	python -X utf8 tools/gen_tiles.py

$(SRC)/levels_data.c: tools/gen_levels.py ../levels.json
	python -X utf8 tools/gen_levels.py

$(BUILD):
	@mkdir -p $(BUILD)

$(BUILD)/%.o: $(SRC)/%.c | $(BUILD)
	$(CC) $(CFLAGS) -c $< -o $@

$(BUILD)/%.o: $(SRC)/%.s | $(BUILD)
	$(AS) $(ASFLAGS) -c $< -o $@

$(BUILD)/$(TARGET).elf: $(OBJS)
	$(CC) $(LDFLAGS) -o $@ $(OBJS) -lgcc
	$(SIZE) $@

$(TARGET).gba: $(BUILD)/$(TARGET).elf
	$(OBJCOPY) -O binary $< $(BUILD)/$(TARGET).bin
	node tools/gbafix.js $(BUILD)/$(TARGET).bin "SOKOBAN"
	node -e "require('fs').copyFileSync('$(BUILD)/$(TARGET).bin','$(TARGET).gba'); console.log('Built $(TARGET).gba')"

clean:
	node -e "const fs=require('fs'); try{fs.rmSync('$(BUILD)',{recursive:true})}catch(e){} try{fs.unlinkSync('$(TARGET).gba')}catch(e){}"

run: $(TARGET).gba
	mgba-qt $(TARGET).gba || mgba $(TARGET).gba || echo "Open sokoban.gba in mGBA"
