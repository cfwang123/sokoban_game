#!/usr/bin/env perl
use strict;
use warnings;
use FindBin;
use lib $FindBin::Bin;
use Game;

# perlapp1 — 推箱子终端版（教学）

my @LEVEL = (
    '#######',
    '#. . .#',
    '# $$$ #',
    '#.$@$.#',
    '# $$$ #',
    '#. . .#',
    '#######',
);

my $state = Game::from_rows(\@LEVEL, 0);
print "sokoban_perl — wasd 移动, z 撤销, r 重置, q 退出\n";

while (1) {
    print "\n";
    print Game::render_ascii($state);
    my $flag = $state->{won} ? ' WIN!' : '';
    print "moves=$state->{moves}$flag\n> ";
    my $line = <STDIN>;
    last unless defined $line;
    chomp $line;
    $line =~ s/^\s+|\s+$//g;
    next if $line eq '';
    my $ch = lc substr($line, 0, 1);
    if    ($ch eq 'w') { Game::try_move($state, 0, -1); }
    elsif ($ch eq 's') { Game::try_move($state, 0, 1); }
    elsif ($ch eq 'a') { Game::try_move($state, -1, 0); }
    elsif ($ch eq 'd') { Game::try_move($state, 1, 0); }
    elsif ($ch eq 'z') { Game::undo($state); }
    elsif ($ch eq 'r') { $state = Game::from_rows(\@LEVEL, 0); }
    elsif ($ch eq 'q') { last; }
    print "Level clear!\n" if $state->{won};
}
