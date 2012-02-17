#! /usr/bin/perl -w
require '/usr/lib/news/innshellvars.pl';

use strict;
use vars qw(%attributes);

use lib "/MUD/mudrpc/perl/lib";
use JSONRequest "/MUD/rpc/perl";

sub access()
{
    my $grplists = funcall("news","get_newsgroups",
	$attributes{'username'});
    my %result = (
	"read" => join(",", @{ $grplists->[0] }),
	"post" => join(",", @{ $grplists->[1] }),
    );
    
    return %result;
}
