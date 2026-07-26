#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"

python3 tools/gen_levels.py

if command -v psp-cmake >/dev/null 2>&1; then
  rm -rf build
  mkdir -p build
  cd build
  psp-cmake ..
  make -j"$(nproc 2>/dev/null || echo 2)"
  cp -f EBOOT.PBP ../EBOOT.PBP
  echo "OK: EBOOT.PBP"
  exit 0
fi

if command -v docker >/dev/null 2>&1; then
  docker pull ghcr.io/pspdev/pspdev:latest
  docker run --rm -v "$PWD:/src" -w /src ghcr.io/pspdev/pspdev:latest \
    bash -lc "python3 tools/gen_levels.py && rm -rf build && mkdir -p build && cd build && psp-cmake .. && make -j\$(nproc) && ls -la"
  cp -f build/EBOOT.PBP ./EBOOT.PBP
  echo "OK: EBOOT.PBP (docker)"
  exit 0
fi

echo "Need pspdev (psp-cmake) or Docker"
exit 1
