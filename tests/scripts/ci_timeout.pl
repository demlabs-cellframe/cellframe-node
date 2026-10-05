#!/usr/bin/perl
# Usage: ci_timeout.pl <seconds> <command> [args...]
# Runs the command in its own process group and kills the whole group on timeout
# (exit 124), so helpers it spawns (ssh/rsync) can't keep a CI job hanging.
# macOS runners have no timeout(1).
use strict;
use warnings;

my $timeout = shift or die "usage: $0 <seconds> <command> [args...]\n";
my $pid = fork;
die "fork failed: $!\n" unless defined $pid;
if (!$pid) {
    setpgrp(0, 0);
    exec @ARGV or exit 127;
}
$SIG{ALRM} = sub {
    kill 'TERM', -$pid;
    sleep 5;
    kill 'KILL', -$pid;
    print STDERR "timed out after ${timeout}s: @ARGV\n";
    exit 124;
};
alarm $timeout;
waitpid($pid, 0);
exit($? & 127 ? 128 + ($? & 127) : $? >> 8);
