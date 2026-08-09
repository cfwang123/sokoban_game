package Game;
use strict;
use warnings;

# 推箱子核心逻辑（Perl 教学）

sub key { return "$_[0],$_[1]"; }

sub from_rows {
    my ($rows, $index) = @_;
    $index //= 0;
    my %walls;
    my %goals;
    my %boxes;
    my ($px, $py) = (0, 0);
    my ($max_x, $max_y) = (0, 0);
    for my $y (0 .. $#$rows) {
        $max_y = $y;
        my $row = $rows->[$y];
        for my $x (0 .. length($row) - 1) {
            $max_x = $x if $x > $max_x;
            my $ch = substr($row, $x, 1);
            my $k = key($x, $y);
            if    ($ch eq '#') { $walls{$k} = 1; }
            elsif ($ch eq '.') { $goals{$k} = 1; }
            elsif ($ch eq '$') { $boxes{$k} = 1; }
            elsif ($ch eq '*') { $boxes{$k} = 1; $goals{$k} = 1; }
            elsif ($ch eq '@') { ($px, $py) = ($x, $y); }
            elsif ($ch eq '+') { ($px, $py) = ($x, $y); $goals{$k} = 1; }
        }
    }
    return {
        walls => \%walls,
        goals => \%goals,
        boxes => \%boxes,
        player => [$px, $py],
        moves => 0,
        won => 0,
        width => $max_x + 1,
        height => $max_y + 1,
        level_index => $index,
        hist => [],
    };
}

sub try_move {
    my ($s, $dx, $dy) = @_;
    return 0 if $s->{won};
    my ($px, $py) = @{ $s->{player} };
    my ($nx, $ny) = ($px + $dx, $py + $dy);
    my $nk = key($nx, $ny);
    return 0 if $s->{walls}{$nk};
    if ($s->{boxes}{$nk}) {
        my ($bx, $by) = ($nx + $dx, $ny + $dy);
        my $bk = key($bx, $by);
        return 0 if $s->{walls}{$bk} || $s->{boxes}{$bk};
        push @{ $s->{hist} }, { player => [$px, $py], box_from => $nk, box_to => $bk };
        delete $s->{boxes}{$nk};
        $s->{boxes}{$bk} = 1;
        $s->{player} = [$nx, $ny];
        $s->{moves}++;
        _check_win($s);
        return 1;
    }
    push @{ $s->{hist} }, { player => [$px, $py], box_from => undef, box_to => undef };
    $s->{player} = [$nx, $ny];
    return 1;
}

sub undo {
    my ($s) = @_;
    return 0 if $s->{won} || !@{ $s->{hist} };
    my $entry;
    while (@{ $s->{hist} }) {
        $entry = pop @{ $s->{hist} };
        last if defined $entry->{box_from};
        $s->{player} = $entry->{player};
    }
    return 1 if !defined $entry || !defined $entry->{box_from};
    $s->{player} = $entry->{player};
    delete $s->{boxes}{ $entry->{box_to} };
    $s->{boxes}{ $entry->{box_from} } = 1;
    $s->{moves}-- if $s->{moves} > 0;
    $s->{won} = 0;
    return 1;
}

sub _check_win {
    my ($s) = @_;
    for my $b (keys %{ $s->{boxes} }) {
        unless ($s->{goals}{$b}) {
            $s->{won} = 0;
            return;
        }
    }
    $s->{won} = 1;
}

sub render_ascii {
    my ($s) = @_;
    my $out = '';
    for my $y (0 .. $s->{height} - 1) {
        for my $x (0 .. $s->{width} - 1) {
            my $k = key($x, $y);
            if ($s->{player}[0] == $x && $s->{player}[1] == $y) {
                $out .= $s->{goals}{$k} ? '+' : '@';
            } elsif ($s->{boxes}{$k}) {
                $out .= $s->{goals}{$k} ? '*' : '$';
            } elsif ($s->{walls}{$k}) {
                $out .= '#';
            } elsif ($s->{goals}{$k}) {
                $out .= '.';
            } else {
                $out .= ' ';
            }
        }
        $out .= "\n";
    }
    return $out;
}

1;
