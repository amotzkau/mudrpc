// This file is part of UNItopia Mudlib.
// ----------------------------------------------------------------
// File:	/secure/rpc/obj/connection.c
// Description:	RPC-Master
// Author:	Gnomi@UNItopia
//

#pragma strict_types

#include <commands.h>
#include <rpc.h>

#define MAX_BPS 65000

string *puffer = ({});

int out;
int last;

int logon()
{
    enable_telnet(0);
    set_prompt("");
    
    add_action("tcp_rpc","RPC", AA_NOSPACE);
    add_action("tcp_ping","PING", AA_NOSPACE);

    return 1;
}

void net_dead()
{
    destruct(this_object());
}

static int tcp_ping(string str)
{
    efun::tell_object(this_object(), "PONG\n");

    return 1;
}

static int tcp_rpc(string str)
{
    if(!str)
	return 1;

    if(sizeof(str) && str[<1] == '$')
        str = str[0..<2];

    RPC_SERVER->receive_tcp(str);

    return 1;
}

private void send_delayed()
{
    int rest;
    
    if(last != time())
    {
	last = time();
	out = 0;
    }
    
    rest = MAX_BPS - out;
        
    while(sizeof(puffer) && rest > 0)
    {
	string msg = puffer[0];
	
	out += sizeof(msg);
	
	efun::tell_object(this_object(), msg[..rest-1]);
	
	if(rest < sizeof(msg))
	{
	    puffer[0] = msg[rest..];
	    break;
	}

        rest -= sizeof(msg);
	puffer = puffer[1..];
    }
    
    if(sizeof(puffer))
    {
	if(find_call_out(#'send_delayed)<0)
	    call_out(#'send_delayed, 1);
    }
}

void send_tcp(string msg)
{
    int rest;
    
    if(object_name(previous_object()) != RPC_SERVER)
	return;

    msg += "\n";
    
    if(sizeof(puffer))
    {
	puffer += ({msg});
	if(find_call_out(#'send_delayed)<0)
	    send_delayed();
	return;
    }
    
    if(last != time())
    {
	last = time();
	out = 0;
    }
    
    rest = MAX_BPS - out;
    out+=sizeof(msg);

    if(rest > 0)
	efun::tell_object(this_object(), msg[..rest-1]);
    else
	rest = 0;
    
    if(rest < sizeof(msg))
    {
	puffer += ({ msg[rest..] });
	if(find_call_out(#'send_delayed)<0)
	    call_out(#'send_delayed, 1);
	return;
    }
}

void catch_tell(string str)
{
    // Disallow any messages from other MUD objects.
}
