# Sokoban · PSP (pspapp1)

> [中文版](README.ZH.md)

Ports `html_app` Sokoban to **PlayStation Portable** homebrew.  
Build style aligned with pspdev + **sceGu** rect drawing (no external textures).

Output: `EBOOT.PBP` (~1MB)

## Run

| Environment | How |
|-------------|-----|
| **Emulator** | [PPSSPP](https://www.ppsspp.org/) → File → Load → `pspapp1/EBOOT.PBP` |
| **Hardware** | copy to `ms0:/PSP/GAME/Sokoban/EBOOT.PBP` (CFW required) |

## Controls

| Input | Action |
|-------|--------|
| **← →** (title) | select level |
| **START / ×** (title) | start |
| **D-pad / analog** | move / push (repeat ok) |
| **○ / □** | undo |
| **SELECT** | reset level |
| **START** (in game) | menu: RESET / NEXT / ANSWER |
| **×** (menu) | confirm |
| **○** (menu) | back |
| **×** (win) | next level |
| **○** (win) | title |
| **○ / START** (DEMO) | cancel solution playback |
| **SELECT** (title) | quit |

## Display

- Resolution **480×272**, cell **24×24**
- Stone walls / wood boxes (highlight + X) / red goals / player
- Camera follows large levels; top HUD (level / moves / boxes)

## Rebuild

### Recommended: WSL Ubuntu + `~/pspdev`

- WSL2 Ubuntu
- [pspdev](https://github.com/pspdev/pspdev) extracted to `~/pspdev`
- `cmake`, `python3` (`sudo apt install cmake build-essential python3` if needed)

**Windows one-shot:**

```bat
cd pspapp1
build_wsl.bat
```

**Or in WSL:**

```bash
export PSPDEV=$HOME/pspdev
export PATH=$PSPDEV/bin:$PATH

cd /mnt/<drive>/.../sokoban/pspapp1   # your repo path under WSL
python3 tools/gen_levels.py
rm -rf build && mkdir build && cd build
psp-cmake .. && make -j$(nproc)
cp -f EBOOT.PBP ../EBOOT.PBP
```

### Alternatives

```bat
cd pspapp1
build.bat
```

```bash
./build.sh
```
