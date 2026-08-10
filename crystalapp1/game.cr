# 推箱子核心逻辑（Crystal 教学）

class Hist
  property px : Int32, py : Int32
  property box_from : String?
  property box_to : String?

  def initialize(@px, @py, @box_from = nil, @box_to = nil)
  end
end

class GameState
  property walls : Set(String)
  property goals : Set(String)
  property boxes : Set(String)
  property px : Int32
  property py : Int32
  property moves : Int32
  property won : Bool
  property width : Int32
  property height : Int32
  property hist : Array(Hist)

  def initialize
    @walls = Set(String).new
    @goals = Set(String).new
    @boxes = Set(String).new
    @px = 0
    @py = 0
    @moves = 0
    @won = false
    @width = 0
    @height = 0
    @hist = [] of Hist
  end

  def self.key(x : Int32, y : Int32) : String
    "#{x},#{y}"
  end

  def self.from_rows(rows : Array(String), index = 0) : GameState
    s = GameState.new
    max_x = 0
    max_y = 0
    rows.each_with_index do |row, y|
      max_y = y
      row.each_char.with_index do |ch, x|
        max_x = x if x > max_x
        k = key(x, y)
        case ch
        when '#' then s.walls << k
        when '.' then s.goals << k
        when '$' then s.boxes << k
        when '*'
          s.boxes << k
          s.goals << k
        when '@'
          s.px = x
          s.py = y
        when '+'
          s.px = x
          s.py = y
          s.goals << k
        end
      end
    end
    s.width = max_x + 1
    s.height = max_y + 1
    s
  end

  def check_win
    @won = @boxes.all? { |b| @goals.includes?(b) }
  end

  def try_move(dx : Int32, dy : Int32) : Bool
    return false if @won
    nx = @px + dx
    ny = @py + dy
    nk = self.class.key(nx, ny)
    return false if @walls.includes?(nk)
    if @boxes.includes?(nk)
      bx = nx + dx
      by = ny + dy
      bk = self.class.key(bx, by)
      return false if @walls.includes?(bk) || @boxes.includes?(bk)
      @hist << Hist.new(@px, @py, nk, bk)
      @boxes.delete(nk)
      @boxes << bk
      @px = nx
      @py = ny
      @moves += 1
      check_win
      return true
    end
    @hist << Hist.new(@px, @py)
    @px = nx
    @py = ny
    true
  end

  def undo : Bool
    return false if @won || @hist.empty?
    while !@hist.empty?
      e = @hist.pop
      if bf = e.box_from
        @px = e.px
        @py = e.py
        @boxes.delete(e.box_to.not_nil!)
        @boxes << bf
        @moves -= 1 if @moves > 0
        @won = false
        return true
      end
      @px = e.px
      @py = e.py
    end
    true
  end

  def render_ascii : String
    String.build do |io|
      @height.times do |y|
        @width.times do |x|
          k = self.class.key(x, y)
          if @px == x && @py == y
            io << (@goals.includes?(k) ? '+' : '@')
          elsif @boxes.includes?(k)
            io << (@goals.includes?(k) ? '*' : '$')
          elsif @walls.includes?(k)
            io << '#'
          elsif @goals.includes?(k)
            io << '.'
          else
            io << ' '
          end
        end
        io << '\n'
      end
    end
  end
end
