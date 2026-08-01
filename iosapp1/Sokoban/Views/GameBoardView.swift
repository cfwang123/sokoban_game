import SwiftUI

/// 棋盘绘制 + 点击点格
///
/// 教学要点：
/// - 用 `Canvas`（iOS 15+）做自定义绘制，类似 Android `onDraw` / HTML Canvas
/// - `DragGesture(minimumDistance: 0)` 模拟 tap 取坐标
struct GameBoardView: View {
    @ObservedObject var model: GameViewModel

    var body: some View {
        GeometryReader { geo in
            let layout = Self.layout(for: model.state, in: geo.size)
            Canvas { context, size in
                guard let s = model.state else { return }
                drawBoard(context: context, state: s, layout: layout)
            }
            .contentShape(Rectangle())
            .gesture(
                DragGesture(minimumDistance: 0)
                    .onEnded { value in
                        guard let s = model.state else { return }
                        let cell = layout.cellSize
                        guard cell > 0 else { return }
                        let gx = Int(floor((value.location.x - layout.offsetX) / cell))
                        let gy = Int(floor((value.location.y - layout.offsetY) / cell))
                        guard gx >= 0, gy >= 0, gx < s.width, gy < s.height else { return }
                        model.onCellTap(gridX: gx, gridY: gy)
                    }
            )
        }
        .background(Color(hex: 0x2D2D44))
        .clipShape(RoundedRectangle(cornerRadius: 8))
    }

    // MARK: - Layout

    struct BoardLayout {
        var cellSize: CGFloat
        var offsetX: CGFloat
        var offsetY: CGFloat
    }

    static func layout(for state: GameState?, in size: CGSize) -> BoardLayout {
        guard let s = state, s.width > 0, s.height > 0 else {
            return BoardLayout(cellSize: 0, offsetX: 0, offsetY: 0)
        }
        let pad = min(size.width, size.height) * 0.03
        let availW = size.width - pad * 2
        let availH = size.height - pad * 2
        let cell = min(availW / CGFloat(s.width), availH / CGFloat(s.height))
        let boardW = cell * CGFloat(s.width)
        let boardH = cell * CGFloat(s.height)
        return BoardLayout(
            cellSize: cell,
            offsetX: (size.width - boardW) / 2,
            offsetY: (size.height - boardH) / 2
        )
    }

    // MARK: - Drawing

    private func drawBoard(context: GraphicsContext, state: GameState, layout: BoardLayout) {
        let cell = layout.cellSize
        guard cell > 0 else { return }

        // 地板
        for y in 0..<state.height {
            for x in 0..<state.width {
                let r = rect(x: x, y: y, layout: layout)
                context.fill(Path(r), with: .color(Color(hex: 0x3A3A55)))
                context.stroke(Path(r), with: .color(Color(hex: 0x444466)), lineWidth: 0.5)
            }
        }

        // 墙
        let edge = max(2, cell * 0.08)
        for key in state.walls {
            guard let (x, y) = parseKey(key) else { continue }
            let r = rect(x: x, y: y, layout: layout)
            context.fill(Path(r), with: .color(Color(hex: 0x4A4A6A)))
            context.fill(Path(CGRect(x: r.minX, y: r.minY, width: r.width, height: edge)), with: .color(Color(hex: 0x5A5A7A)))
            context.fill(Path(CGRect(x: r.minX, y: r.minY, width: edge, height: r.height)), with: .color(Color(hex: 0x5A5A7A)))
            context.fill(Path(CGRect(x: r.minX, y: r.maxY - edge, width: r.width, height: edge)), with: .color(Color(hex: 0x2A2A4A)))
            context.fill(Path(CGRect(x: r.maxX - edge, y: r.minY, width: edge, height: r.height)), with: .color(Color(hex: 0x2A2A4A)))
        }

        // 目标点
        for key in state.goals {
            guard let (x, y) = parseKey(key) else { continue }
            let r = rect(x: x, y: y, layout: layout)
            let c = CGPoint(x: r.midX, y: r.midY)
            let rad = cell * 0.15
            let circle = Path(ellipseIn: CGRect(x: c.x - rad, y: c.y - rad, width: rad * 2, height: rad * 2))
            context.fill(circle, with: .color(Color(hex: 0xE94560)))
            context.stroke(circle, with: .color(Color(hex: 0xFF6B81)), lineWidth: 2)
        }

        // 箱子
        for key in state.boxes {
            guard let (x, y) = parseKey(key) else { continue }
            let onGoal = state.isGoal(x: x, y: y)
            let r = rect(x: x, y: y, layout: layout).insetBy(dx: cell * 0.1, dy: cell * 0.1)
            let fill = onGoal ? Color(hex: 0x2ECC71) : Color(hex: 0xF39C12)
            let stroke = onGoal ? Color(hex: 0x27AE60) : Color(hex: 0xE67E22)
            let cross = onGoal ? Color(hex: 0x1E8449) : Color(hex: 0xD35400)
            context.fill(Path(roundedRect: r, cornerRadius: 4), with: .color(fill))
            context.stroke(Path(roundedRect: r, cornerRadius: 4), with: .color(stroke), lineWidth: 2)
            var h = Path()
            h.move(to: CGPoint(x: r.midX - r.width * 0.18, y: r.midY))
            h.addLine(to: CGPoint(x: r.midX + r.width * 0.18, y: r.midY))
            h.move(to: CGPoint(x: r.midX, y: r.midY - r.height * 0.18))
            h.addLine(to: CGPoint(x: r.midX, y: r.midY + r.height * 0.18))
            context.stroke(h, with: .color(cross), lineWidth: 2)
        }

        // 玩家
        let p = state.player
        let pr = rect(x: p.x, y: p.y, layout: layout)
        let c = CGPoint(x: pr.midX, y: pr.midY)
        let rad = cell * 0.35
        let body = Path(ellipseIn: CGRect(x: c.x - rad, y: c.y - rad, width: rad * 2, height: rad * 2))
        context.fill(body, with: .color(Color(hex: 0x3498DB)))
        context.stroke(body, with: .color(Color(hex: 0x2980B9)), lineWidth: 2)
        let eyeR = cell * 0.07
        let eyeY = c.y - cell * 0.08
        for sign: CGFloat in [-1, 1] {
            let ex = c.x + sign * cell * 0.1
            let eye = Path(ellipseIn: CGRect(x: ex - eyeR, y: eyeY - eyeR, width: eyeR * 2, height: eyeR * 2))
            context.fill(eye, with: .color(.white))
            let pupil = Path(ellipseIn: CGRect(x: ex - eyeR * 0.5, y: eyeY - eyeR * 0.5, width: eyeR, height: eyeR))
            context.fill(pupil, with: .color(Color(hex: 0x1A1A2E)))
        }
    }

    private func rect(x: Int, y: Int, layout: BoardLayout) -> CGRect {
        CGRect(
            x: layout.offsetX + CGFloat(x) * layout.cellSize,
            y: layout.offsetY + CGFloat(y) * layout.cellSize,
            width: layout.cellSize,
            height: layout.cellSize
        )
    }

    private func parseKey(_ key: String) -> (Int, Int)? {
        let parts = key.split(separator: ",")
        guard parts.count == 2, let x = Int(parts[0]), let y = Int(parts[1]) else { return nil }
        return (x, y)
    }
}

// MARK: - Color helper

extension Color {
    init(hex: UInt32, alpha: Double = 1) {
        let r = Double((hex >> 16) & 0xFF) / 255
        let g = Double((hex >> 8) & 0xFF) / 255
        let b = Double(hex & 0xFF) / 255
        self.init(.sRGB, red: r, green: g, blue: b, opacity: alpha)
    }
}
