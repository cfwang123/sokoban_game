# 推箱子 · PSP 版（pspapp1）

> [English](README.md)


将 `html_app` 推箱子移植为 **PlayStation Portable** homebrew。  
构建与工程风格对齐 `starstrike`（**pspdev** + **sceGu** 矩形绘制，无外部贴图）。

成品：`EBOOT.PBP`（约 1MB）

## 运行

| 环境 | 方法 |
|------|------|
| **模拟器** | [PPSSPP](https://www.ppsspp.org/) → File → Load → `pspapp1/EBOOT.PBP` |
| **实机** | 复制到 `ms0:/PSP/GAME/Sokoban/EBOOT.PBP`（需 CFW） |

## 操作

| 按键 | 功能 |
|------|------|
| **← →**（标题） | 选关 |
| **START / ×**（标题） | 开始 |
| **十字键 / 摇杆** | 移动 / 推箱（可连发） |
| **○ / □** | 撤销 |
| **SELECT** | 重置本关 |
| **START**（游戏中） | 菜单：RESET / NEXT / ANSWER |
| **×**（菜单） | 确认 |
| **○**（菜单） | 返回 |
| **×**（过关） | 下一关 |
| **○**（过关） | 回标题 |
| **○ / START**（DEMO） | 取消答案回放 |
| **SELECT**（标题） | 退出 |

## 画面

- 分辨率 **480×272**，格子 **24×24**
- 石砖墙 / 木箱（高光+X）/ 红色目标 / 小人
- 大关卡镜头跟随，顶部 HUD（关卡 / 步数 / 箱子）

## 重新编译

### 推荐：WSL Ubuntu + `~/pspdev`

依赖：

- WSL2 Ubuntu
- 已解压的 [pspdev](https://github.com/pspdev/pspdev) 到 `~/pspdev`
- `cmake`、`python3`（无则：`sudo apt install cmake build-essential python3`）

**Windows 一键：**

```bat
cd pspapp1
build_wsl.bat
```

**或在 WSL 终端：**

```bash
export PSPDEV=$HOME/pspdev
export PATH=$PSPDEV/bin:$PATH

# 建议写入 ~/.bashrc
# export PSPDEV=$HOME/pspdev
# export PATH=$PSPDEV/bin:$PATH

cd /mnt/<盘符>/.../sokoban/pspapp1   # 改成你的仓库在 WSL 下的路径
python3 tools/gen_levels.py
rm -rf build && mkdir build && cd build
psp-cmake .. && make -j$(nproc)
cp -f EBOOT.PBP ../EBOOT.PBP
```

成功后根目录生成 / 更新 `EBOOT.PBP`。

### 备选：Docker

依赖：Docker Desktop 已启动（可开启 WSL 集成）

```bat
cd pspapp1
build.bat
```

### 备选：本机 Linux + pspdev

```bash
./build.sh
```

## 工程结构

```
pspapp1/
  EBOOT.PBP           成品 ROM 包
  build_wsl.bat       WSL + ~/pspdev 一键编译（推荐）
  build.bat           Docker 编译
  build.sh            Linux / 本机 pspdev
  CMakeLists.txt      现代 pspdev 构建
  Makefile            经典 build.mak
  include/            gfx / font / game / levels
  src/
    main.c            入口、HOME 回调
    gfx.c             sceGu 初始化与矩形
    font.c            5×7 点阵字
    game.c            推箱子逻辑 + 分层绘制
    levels_data.c     关卡数据（脚本生成，勿手改）
  tools/
    gen_levels.py     从 ../levels.json 打包关卡与答案
  build/              中间产物（可删）
```

## 技术说明

| 项目 | 内容 |
|------|------|
| 平台 | PSP homebrew（USER 模式） |
| 图形 | **sceGu** 2D 矩形（无需外部贴图） |
| 输入 | `sceCtrl` + 模拟摇杆 |
| 工具链 | **pspdev**（WSL `~/pspdev`）或 Docker `ghcr.io/pspdev/pspdev` |
| 关卡 | 约 60 关，优先收录带答案关卡 |

## 与其它版本

| 目录 | 平台 |
|------|------|
| `html_app/` | 浏览器 2D |
| `fcapp1/` | FC / NES |
| `gbaapp1/` | GBA |
| `pspapp1/` | **PSP（本目录）** |
