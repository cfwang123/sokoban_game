import Foundation

/// 单关元数据（对应 levels.json 中的一项）
struct LevelData: Identifiable, Codable, Equatable {
    let id: Int
    let name: String
    let puzzle: [String]
    /// 内置解法：U/D/L/R 字符串；无解法时为 nil
    let solution: String?

    var hasSolution: Bool {
        guard let s = solution else { return false }
        return !s.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty
    }

    /// 兼容 solution 为 JSON null 或空串
    enum CodingKeys: String, CodingKey {
        case id, name, puzzle, solution
    }

    init(id: Int, name: String, puzzle: [String], solution: String?) {
        self.id = id
        self.name = name
        self.puzzle = puzzle
        self.solution = solution
    }

    init(from decoder: Decoder) throws {
        let c = try decoder.container(keyedBy: CodingKeys.self)
        id = try c.decodeIfPresent(Int.self, forKey: .id) ?? 0
        name = try c.decodeIfPresent(String.self, forKey: .name) ?? "Level"
        puzzle = try c.decode([String].self, forKey: .puzzle)
        if c.contains(.solution), try !c.decodeNil(forKey: .solution) {
            let s = try c.decode(String.self, forKey: .solution)
            solution = s.isEmpty ? nil : s
        } else {
            solution = nil
        }
    }
}
