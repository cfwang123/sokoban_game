import SwiftUI

/// 主界面：图标工具栏 + 棋盘 + 方向键（对齐 androidapp1 紧凑布局）
struct ContentView: View {
    @StateObject private var model = GameViewModel()

    var body: some View {
        ZStack {
            Color(hex: 0x1A1A2E).ignoresSafeArea()

            VStack(spacing: 4) {
                toolbar
                Text(model.statusText)
                    .font(.system(size: 11))
                    .foregroundStyle(Color(hex: 0xAAAAAA))
                    .frame(maxWidth: .infinity)
                    .frame(minHeight: 14)

                GameBoardView(model: model)
                    .frame(maxWidth: .infinity, maxHeight: .infinity)

                DPadView(model: model)
                    .padding(.bottom, 8)
            }
            .padding(.horizontal, 6)
            .padding(.top, 4)

            if model.showWin {
                winOverlay
            }
        }
        .preferredColorScheme(.dark)
        .alert("操作说明", isPresented: $model.showHelp) {
            Button("关闭", role: .cancel) {}
        } message: {
            Text("""
            • 点击空地：自动走到该位置
            • 点击相邻箱子：向前推一格
            • 虚拟方向键：移动 / 推箱
            • 撤销：只撤销推箱子的步
            • 重置：重开本关
            • 查看答案：回放内置解法（如有）
            • 上一关 / 下一关：切换关卡
            """)
        }
    }

    // MARK: - Toolbar（图标按钮，单行）

    private var toolbar: some View {
        HStack(spacing: 3) {
            iconButton(systemName: "chevron.left", label: "上一关") {
                model.goPrevLevel()
            }

            // 关卡选择：iOS 用 Menu / Picker
            if !model.levels.isEmpty {
                Picker("关卡", selection: $model.selectedLevelIndex) {
                    ForEach(0..<model.levels.count, id: \.self) { i in
                        Text(model.levelPickerLabels[i]).tag(i)
                    }
                }
                .pickerStyle(.menu)
                .tint(Color(hex: 0xEEEEEE))
                .frame(maxWidth: .infinity)
                .onChange(of: model.selectedLevelIndex) { newValue in
                    if model.state?.levelIndex != newValue {
                        model.loadLevel(newValue)
                    }
                }
            } else {
                Spacer()
            }

            Text(model.movesText)
                .font(.system(size: 12, weight: .medium, design: .monospaced))
                .foregroundStyle(Color(hex: 0xAAAAAA))
                .frame(minWidth: 24)

            iconButton(systemName: "arrow.uturn.backward", label: "撤销") {
                model.undo()
            }
            iconButton(systemName: "arrow.clockwise", label: "重置") {
                model.resetLevel()
            }
            iconButton(
                systemName: model.answerActive ? "stop.fill" : "lightbulb.fill",
                label: model.answerActive ? "停止查看" : "查看答案",
                accent: true,
                enabled: model.answerActive || model.canViewAnswer
            ) {
                model.toggleAnswer()
            }
            iconButton(systemName: "questionmark.circle", label: "帮助") {
                model.showHelp = true
            }
            iconButton(systemName: "chevron.right", label: "下一关") {
                model.goNextLevel()
            }
        }
        .padding(.horizontal, 2)
    }

    private func iconButton(
        systemName: String,
        label: String,
        accent: Bool = false,
        enabled: Bool = true,
        action: @escaping () -> Void
    ) -> some View {
        Button(action: action) {
            Image(systemName: systemName)
                .font(.system(size: 15, weight: .semibold))
                .foregroundStyle(Color(hex: 0xEEEEEE).opacity(enabled ? 1 : 0.4))
                .frame(width: 36, height: 36)
                .background(accent ? Color(hex: 0xE94560) : Color(hex: 0x0F3460))
                .overlay(
                    RoundedRectangle(cornerRadius: 8)
                        .stroke(Color(hex: 0x533483), lineWidth: accent ? 0 : 1)
                )
                .clipShape(RoundedRectangle(cornerRadius: 8))
        }
        .disabled(!enabled)
        .accessibilityLabel(label)
        .buttonStyle(.plain)
    }

    // MARK: - Win

    private var winOverlay: some View {
        ZStack {
            Color.black.opacity(0.7).ignoresSafeArea()
            VStack(spacing: 12) {
                Text("恭喜过关！")
                    .font(.system(size: 22, weight: .bold))
                    .foregroundStyle(Color(hex: 0xE94560))
                Text("共用 \(model.state?.moves ?? 0) 步完成！")
                    .foregroundStyle(Color(hex: 0xAAAAAA))
                Button {
                    model.goNextLevel()
                } label: {
                    Image(systemName: "chevron.right")
                        .font(.system(size: 20, weight: .bold))
                        .foregroundStyle(.white)
                        .frame(width: 52, height: 52)
                        .background(Color(hex: 0xE94560))
                        .clipShape(RoundedRectangle(cornerRadius: 8))
                }
                .accessibilityLabel("下一关")
                .padding(.top, 4)
            }
            .padding(28)
            .background(Color(hex: 0x16213E))
            .clipShape(RoundedRectangle(cornerRadius: 16))
        }
    }
}

#Preview {
    ContentView()
}
