# Sokoban iOS (iosapp1) — teaching demo

> [中文版](readme.zh.md)

SwiftUI iOS sources for the Sokoban logic from [`html_app`](../html_app) / [`androidapp1`](../androidapp1), as a **teaching demo of iOS app structure**.

[Changelog](CHANGELOG.md)

**Current version: 1.0.0**

> **Note**  
> - Complete readable Swift sources and assets; **Xcode build is not required inside this repo**.  
> - On a Mac, create an Xcode project as below, add these files, then run on simulator/device.  
> - Windows cannot build iOS locally; sources remain readable for study.

---

## 1. How is an iOS app built?

| Step | What | In this project |
|------|------|-----------------|
| 1. Install tools | Mac + [Xcode](https://developer.apple.com/xcode/) (iOS SDK, simulators) | — |
| 2. New project | Xcode → File → New → Project → **App**; Interface: **SwiftUI**; Language: **Swift** | entry: `SokobanApp.swift` |
| 3. UI | SwiftUI `View` describes UI; state changes refresh automatically | `ContentView` / `GameBoardView` / `DPadView` |
| 4. Logic | pure Swift types, decoupled from UI | `Game/` — `GameState`, `Pathfinding`, … |
| 5. Assets | JSON/images into **Bundle** | `Resources/levels.json` |
| 6. Run | simulator or device → Run (⌘R) | done in Xcode |
| 7. Ship (optional) | signing, Archive, App Store Connect | out of scope here |

vs **Android**:

| Concept | Android (`androidapp1`) | iOS (`iosapp1`) |
|---------|-------------------------|-----------------|
| Build | Gradle (`build.gradle.kts`) | Xcode / SwiftPM |
| Entry | `MainActivity` | `@main struct SokobanApp: App` |
| Layout | XML + ViewBinding | SwiftUI `View` |
| Custom draw | `GameBoardView` Canvas `onDraw` | SwiftUI `Canvas` |
| State refresh | manual `invalidate` / mutate UI | `@Published` + `ObservableObject` |
| Persistence | `SharedPreferences` | `UserDefaults` |
| Resources | `assets/` / `res/` | Bundle / Asset Catalog |
| System icons | Vector drawable | **SF Symbols** (`Image(systemName:)`) |

---

## 2. Run on Mac with these sources (optional)

1. Open Xcode → **Create a new Xcode project** → **iOS App**  
   - Product Name: `Sokoban`  
   - Interface: **SwiftUI**  
   - Language: **Swift**  
   - Bundle ID of your choice, e.g. `com.example.sokoban`
2. Delete Xcode sample `ContentView` / `*App` if they conflict with files below.
3. Drag all `.swift` files and `Resources/levels.json` from `iosapp1/Sokoban/` into the project; enable **Copy items if needed** and your App target.
4. Ensure `levels.json` is in Target → **Build Phases → Copy Bundle Resources**.
5. Pick an iPhone simulator → **Run**.

Suggested minimum: **iOS 16+** (newer SwiftUI APIs; lower targets may need small `onChange` tweaks).

---

## 3. Layout

```
iosapp1/
├── readme.md / readme.zh.md
├── CHANGELOG.md
├── .gitignore
└── Sokoban/
    ├── SokobanApp.swift      # @main entry
    ├── ContentView.swift     # main UI: toolbar / board / D-pad / win
    ├── Info.plist            # display name, portrait, etc. (demo)
    ├── Game/                 # UI-decoupled game core
    │   ├── Direction.swift
    │   ├── LevelData.swift
    │   ├── LevelRepository.swift
    │   ├── GameState.swift
    │   ├── Pathfinding.swift
    │   └── GameViewModel.swift   # ObservableObject, drives UI
    ├── Views/
    │   ├── GameBoardView.swift   # Canvas draw + tap
    │   └── DPadView.swift        # virtual D-pad
    └── Resources/
        └── levels.json           # same source as repo root levels.json
```

### Suggested reading order

1. `SokobanApp.swift` — app lifecycle  
2. `ContentView.swift` — how the UI is composed  
3. `GameViewModel.swift` — user action → state → UI refresh  
4. `GameState.swift` / `Pathfinding.swift` — same rules as Android/web  
5. `GameBoardView.swift` — custom draw and touch coordinate mapping  

---

## 4. Features (aligned with android / html)

| Feature | Notes |
|---------|--------|
| All levels | load `levels.json` from Bundle |
| Tap empty floor | `Pathfinding` BFS → walk path |
| Tap adjacent box | `tryMove` push one step |
| Virtual D-pad | SF Symbol + hold to repeat |
| Undo / reset | undo through box pushes only |
| Solution | `Timer` steps through `solution` |
| Level memory | `UserDefaults` |
| Icon toolbar | single row, no horizontal scroll |

---

## 5. SwiftUI style notes

- **Unidirectional data flow**: `View` only reads `@Published` on the view model; events call view-model methods.  
- **Value vs reference**: level data as `struct`; mutable board `GameState` as `class` for in-place updates.  
- **Main-thread UI**: `@MainActor` on `GameViewModel`.  
- **Accessibility**: icon buttons set `accessibilityLabel` for VoiceOver.  

---

## 6. Sync levels

After root `levels.json` updates:

```bash
cp ../levels.json Sokoban/Resources/levels.json
```

---

## References

- Gameplay: [`../html_app`](../html_app)  
- Android: [`../androidapp1`](../androidapp1)  
- [SwiftUI docs](https://developer.apple.com/documentation/swiftui)  
- [SF Symbols](https://developer.apple.com/sf-symbols/)  
