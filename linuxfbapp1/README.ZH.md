# linuxfbapp1 — Linux 帧缓冲推箱子（教学）

> [English](readme.md)


读写 `/dev/fb0` 画色块；无权限或失败时回退终端 ASCII。

```bash
cd linuxfbapp1
make
# 可能需要: sudo ./sokoban_fb
# 或仅 ASCII: 无 fb 时自动降级
```

键位：WASD、Z 撤销、R 重置、N 下一关、Q 退出。
