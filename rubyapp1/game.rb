# frozen_string_literal: true

# 推箱子核心逻辑（Ruby 教学）

class GameState
  attr_reader :walls, :goals, :boxes, :player, :moves, :won, :width, :height, :level_index

  def self.from_rows(rows, index = 0)
    new(rows, index)
  end

  def initialize(rows, index = 0)
    @walls = {}
    @goals = {}
    @boxes = {}
    @player = [0, 0]
    @moves = 0
    @won = false
    @level_index = index
    @hist = []
    max_x = 0
    max_y = 0
    rows.each_with_index do |row, y|
      max_y = y
      row.each_char.with_index do |ch, x|
        max_x = x if x > max_x
        k = key(x, y)
        case ch
        when '#' then @walls[k] = true
        when '.' then @goals[k] = true
        when '$' then @boxes[k] = true
        when '*'
          @boxes[k] = true
          @goals[k] = true
        when '@' then @player = [x, y]
        when '+'
          @player = [x, y]
          @goals[k] = true
        end
      end
    end
    @width = max_x + 1
    @height = max_y + 1
  end

  def try_move(dx, dy)
    return false if @won

    px, py = @player
    nx = px + dx
    ny = py + dy
    nk = key(nx, ny)
    return false if @walls[nk]

    if @boxes[nk]
      bx = nx + dx
      by = ny + dy
      bk = key(bx, by)
      return false if @walls[bk] || @boxes[bk]

      @hist << { player: @player.dup, box_from: nk, box_to: bk }
      @boxes.delete(nk)
      @boxes[bk] = true
      @player = [nx, ny]
      @moves += 1
      check_win
      return true
    end

    @hist << { player: @player.dup, box_from: nil, box_to: nil }
    @player = [nx, ny]
    true
  end

  def undo
    return false if @won || @hist.empty?

    entry = nil
    until @hist.empty?
      entry = @hist.pop
      break if entry[:box_from]

      @player = entry[:player]
    end
    return true if entry.nil? || entry[:box_from].nil?

    @player = entry[:player]
    @boxes.delete(entry[:box_to])
    @boxes[entry[:box_from]] = true
    @moves -= 1 if @moves.positive?
    @won = false
    true
  end

  def render_ascii
    lines = []
    @height.times do |y|
      row = +''
      @width.times do |x|
        k = key(x, y)
        row << if @player == [x, y]
                 @goals[k] ? '+' : '@'
               elsif @boxes[k]
                 @goals[k] ? '*' : '$'
               elsif @walls[k]
                 '#'
               elsif @goals[k]
                 '.'
               else
                 ' '
               end
      end
      lines << row
    end
    "#{lines.join("\n")}\n"
  end

  private

  def key(x, y)
    "#{x},#{y}"
  end

  def check_win
    @won = @boxes.keys.all? { |b| @goals[b] }
  end
end
