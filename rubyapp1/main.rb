#!/usr/bin/env ruby
# frozen_string_literal: true

# rubyapp1 — 推箱子终端版（教学）

require_relative 'game'

LEVEL = [
  '#######',
  '#. . .#',
  '# $$$ #',
  '#.$@$.#',
  '# $$$ #',
  '#. . .#',
  '#######'
].freeze

state = GameState.from_rows(LEVEL, 0)
puts 'sokoban_ruby — wasd 移动, z 撤销, r 重置, q 退出'

loop do
  puts
  print state.render_ascii
  flag = state.won ? ' WIN!' : ''
  print "moves=#{state.moves}#{flag}\n> "
  line = $stdin.gets
  break if line.nil?

  line = line.strip
  next if line.empty?

  case line[0].downcase
  when 'w' then state.try_move(0, -1)
  when 's' then state.try_move(0, 1)
  when 'a' then state.try_move(-1, 0)
  when 'd' then state.try_move(1, 0)
  when 'z' then state.undo
  when 'r' then state = GameState.from_rows(LEVEL, 0)
  when 'q' then break
  end
  puts 'Level clear!' if state.won
end
