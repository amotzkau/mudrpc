#! /usr/bin/perl

use Mail::Address;
use strict;
use vars qw(%hdr $user $modify_headers);

sub filter_post()
{
    my @ngs = split /\s*,\s*/,$hdr{'Newsgroups'};
    
    return "Crossposting is not allowed." if(scalar(@ngs)!=1);

    my $ng = $ngs[0];
    my $name = ucfirst($user);
    
    if($ng =~ !/^mud\./)
    {
        # Add "@MUD" to the name for non-local groups.
	$name .= '@MUD';
    }
    
    my ($addr) = Mail::Address->parse($hdr{'From'});
    $hdr{'From'} = Mail::Address->new($name,$addr->address())->format();
    $hdr{'X-Muduser'} = $name;
    $hdr{'X-Mud'} = 'MUD';
    $modify_headers = 1;
    return "";
}
