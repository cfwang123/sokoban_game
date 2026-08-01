import SwiftUI

/// 虚拟方向键（SF Symbol 图标 + 长按连发）
///
/// 教学要点：
/// - 用 `DragGesture(minimumDistance: 0)` 模拟按下/抬起（类似 Android OnTouch）
/// - 按下立刻走一步，延迟后定时重复（对齐 html_app 键盘按住）
struct DPadView: View {
    @ObservedObject var model: GameViewModel

    var body: some View {
        VStack(spacing: 4) {
            HoldIconButton(systemName: "chevron.up", accessibilityLabel: "上") {
                model.tryDirectionalMove(.up)
            }
            HStack(spacing: 4) {
                HoldIconButton(systemName: "chevron.left", accessibilityLabel: "左") {
                    model.tryDirectionalMove(.left)
                }
                HoldIconButton(systemName: "chevron.down", accessibilityLabel: "下") {
                    model.tryDirectionalMove(.down)
                }
                HoldIconButton(systemName: "chevron.right", accessibilityLabel: "右") {
                    model.tryDirectionalMove(.right)
                }
            }
        }
    }
}

/// 图标按钮：按下立刻回调，按住后按间隔重复
struct HoldIconButton: View {
    let systemName: String
    let accessibilityLabel: String
    let action: () -> Void

    @State private var holdWorkItem: DispatchWorkItem?
    @State private var repeatTimer: Timer?
    @State private var isHolding = false

    private let holdDelay: TimeInterval = 0.18
    private let holdInterval: TimeInterval = 0.09

    var body: some View {
        Image(systemName: systemName)
            .font(.system(size: 18, weight: .bold))
            .foregroundStyle(Color(hex: 0xEEEEEE))
            .frame(width: 48, height: 44)
            .background(Color(hex: 0x0F3460))
            .overlay(
                RoundedRectangle(cornerRadius: 10)
                    .stroke(Color(hex: 0x533483), lineWidth: 1)
            )
            .clipShape(RoundedRectangle(cornerRadius: 10))
            .contentShape(Rectangle())
            .gesture(
                DragGesture(minimumDistance: 0)
                    .onChanged { _ in
                        guard !isHolding else { return }
                        isHolding = true
                        action()
                        let work = DispatchWorkItem {
                            let t = Timer.scheduledTimer(withTimeInterval: holdInterval, repeats: true) { _ in
                                action()
                            }
                            // 保证在主 RunLoop 中触发
                            RunLoop.main.add(t, forMode: .common)
                            repeatTimer = t
                        }
                        holdWorkItem = work
                        DispatchQueue.main.asyncAfter(deadline: .now() + holdDelay, execute: work)
                    }
                    .onEnded { _ in
                        holdWorkItem?.cancel()
                        holdWorkItem = nil
                        repeatTimer?.invalidate()
                        repeatTimer = nil
                        isHolding = false
                    }
            )
            .accessibilityLabel(accessibilityLabel)
    }
}
