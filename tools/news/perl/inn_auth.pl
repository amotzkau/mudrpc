#! /usr/bin/perl -w
require '/usr/lib/news/innshellvars.pl';

use strict;
use vars qw(%attributes);

use lib "/MUD/mudrpc/perl/lib";
use JSONRequest "/MUD/rpc/perl";

sub auth_init()
{
}

sub authenticate()
{
    my $res = funcall("mud","password",$attributes{'username'},$attributes{'password'},'usenet');
    
    return (502, $res || "Incorrect username or password.") if($res==0);
    return (281, "");
}
