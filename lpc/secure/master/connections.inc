// ----------------------------------------------------------------
// File:	/secure/master/connections.inc
// Description:	Connection handling
// Author:	Gnomi@UNItopia
//

/*
 * This example uses TCP port 33033 for communicating with the RPC daemon.
 */

#include "/sys/rpc.h"

#pragma strict_types

// When using TCP connections:
protected object connect()
{
    if(efun::query_mud_port() == 33033 && efun::query_ip_number()=="127.0.0.1")
	return clone_object(RPC_CONNECTION);

    return clone_object(LOGIN_OB);
}

// When using UDP connections:
protected void receive_udp(string host, string msg, int port)
{
    if(msg[0..2] == "RPC")
        RPC_SERVER->receive_udp(host, msg, port);
    else
    {
        //...
    }
}
