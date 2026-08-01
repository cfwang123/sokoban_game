import Foundation

/// 四向移动（与 html_app / androidapp1 的方向编码一致：U D L R）
enum Direction: CaseIterable {
    case up, down, left, right

    var dx: Int {
        switch self {
        case .left: return -1
        case .right: return 1
        default: return 0
        }
    }

    var dy: Int {
        switch self {
        case .up: return -1
        case .down: return 1
        default: return 0
        }
    }

    var code: Character {
        switch self {
        case .up: return "U"
        case .down: return "D"
        case .left: return "L"
        case .right: return "R"
        }
    }

    static func from(code: Character) -> Direction? {
        switch code.uppercased().first {
        case "U": return .up
        case "D": return .down
        case "L": return .left
        case "R": return .right
        default: return nil
        }
    }
}
