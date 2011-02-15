package JSONRequest;

use strict;
use warnings;

use Socket;
use IO::Handle;
use JSON;

our $SOCKETNAME;

sub import
{
    my ($package, $socket) = @_;
    $SOCKETNAME = $socket;
    *{main::funcall} = \&funcall;
}

my $RPCFail = 0;
my $RPCAnswer = 1;
my $RPCRequest = 2;

sub funcall
{
    my ($app, $fun, @args) = @_;

    socket(RPCSocket, AF_UNIX, SOCK_STREAM, PF_UNSPEC);
    connect(RPCSocket, pack_sockaddr_un($SOCKETNAME)) or die "Can't connect.\n";
    RPCSocket->autoflush(1);

    print RPCSocket to_json([ $RPCRequest, 0, $app, $fun, @args ]),"\n";
    my $result = from_json(readline(*RPCSocket));

    close(RPCSocket);

    if($result->[0] == $RPCFail)
    {
        print $result->[2];
        return undef;
    }

    return $result->[2];
}
