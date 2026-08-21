# Sokoban Android (androidapp1)

> [中文版](README.ZH.md)

Native Android port of the [`html_app`](../html_app) 2D web Sokoban.

[Changelog](CHANGELOG.md)

**Current version: 1.0.0**

## Features

| Feature | Notes |
|---------|--------|
| Levels | All levels (`assets/levels.json`, same source as repo root `levels.json`) |
| Tap empty floor | BFS pathfinding to reachable cells |
| Tap box | Push adjacent box one step |
| Virtual D-pad | Tap one step; hold to repeat |
| Undo / reset | Undo rewinds through box pushes (same as web) |
| Solution | Levels with `solution` can animate / stop playback |
| Level switch | Prev / next / dropdown |
| Win | Overlay + next level |
| Progress | SharedPreferences remembers last level |

## UI

- Top **single-row icon toolbar**: prev · level · moves · undo · reset · solution · help · next (no horizontal scroll)
- Bottom **icon D-pad**
- Dark theme (aligned with web colors)

## Tech

| Item | Value |
|------|--------|
| Package | `com.whj.sokoban` |
| Language | Kotlin |
| minSdk | 24 (Android 7.0+) |
| targetSdk / compileSdk | 34 |
| Build | Gradle 8.4 + AGP 8.3.2 + ViewBinding |
| JDK | 17+ |

## Layout

```
androidapp1/
├── app/src/main/
│   ├── assets/levels.json
│   ├── java/com/whj/sokoban/
│   │   ├── MainActivity.kt
│   │   ├── game/              # GameState / Pathfinding / LevelRepository
│   │   └── ui/GameBoardView.kt
│   └── res/
├── CHANGELOG.md
├── README.md / README.ZH.md
├── build.gradle.kts
└── settings.gradle.kts
```

## Build

Requires Android SDK and JDK 17+. Create local `local.properties` with `sdk.dir` (gitignored; do not commit).

```bat
cd androidapp1
gradlew.bat assembleDebug
```

Debug APK: `app/build/outputs/apk/debug/app-debug.apk`

```bat
gradlew.bat assembleRelease
```

Release APK name: `sokoban{versionName}.apk` (e.g. `sokoban1.0.0.apk`).

Install on a connected device:

```bat
adb install -r app\build\outputs\apk\debug\app-debug.apk
adb shell am start -n com.whj.sokoban/.MainActivity
```

## Sync levels

If root `levels.json` changes, overwrite assets:

```bat
copy /Y ..\levels.json app\src\main\assets\levels.json
```

## References

- Gameplay: [`../html_app`](../html_app)
- Repo overview: [`../README.md`](../README.md) · [`../README.ZH.md`](../README.ZH.md)
