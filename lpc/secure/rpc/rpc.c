// ----------------------------------------------------------------
// File:	/secure/rpc/rpc.c
// Description:	RPC master
// Author:	Gnomi
//

#pragma strict_types

#include <error.h>
#include <rpc.h>

#define UDPPACKETSIZE 1024

// Same defines as in Python or Perl
#define RPC_FAIL	0
#define RPC_ANSWER	1
#define RPC_REQUEST	2

mapping state = ([:2]);
#define S_MSG	0
#define S_TIME	1

mapping requests = ([:3]); // ID -> Callback on success, on error, call time
#define REQ_CB_SUCCESS  0
#define REQ_CB_ERROR    1
#define REQ_STARTTIME   2

mapping apps = ([
    "mud":	"/secure/rpc/app",
    "control":	"/secure/rpc/rpc",
    "ftpd":	"/secure/rpc/ftpd",
    "mail":	"/secure/rpc/mail",
    ]);

object daemon;

static void call(closure cb, mixed* args)
{
    // Control-Applikation
    
    switch(args[0])
    {
	case "register_daemon":
	    daemon = previous_object(1);
	    funcall(cb, 0);
	    break;
    }
}

private void exec_msg(string msg, closure callback)
{
    mixed val, res;

    if(catch(val = restore_value("#1:0\n"+msg+"\n")) ||
	!pointerp(val) || sizeof(val)<2)
    {
	do_error("RPC failure: wrong format.\n"+msg+"\n");
	return;
    }

    switch(val[0])
    {
	case RPC_ANSWER:
	    if(member(requests, val[1]))
	    {
		closure cb = requests[val[1], REQ_CB_SUCCESS];
		m_delete(requests, val[1]);
		funcall(cb, val[2]);
	    }
	    break;
	
	case RPC_FAIL:
	{
	    closure cb = requests[val[1], REQ_CB_SUCCESS];
	    closure cbe = requests[val[1], REQ_CB_ERROR];
	    m_delete(requests, val[1]);
	    if(!cbe)
	        do_my_error(sprintf("RPC failure: %s\nCallback: %Q\n", val[2], cb));
	    else
	        funcall(cbe, val[2]);
	    break;
	}
	
	case RPC_REQUEST:
	    if(member(apps, val[2]))
	    {
		string errmsg;
		
		closure cb = lambda(({'res}),
		    ({ #'funcall, callback, 
			({ #'[, ({ #'explode, ({ #'save_value,
			    ({ #'({, RPC_ANSWER, val[1], 'res }),
			}), "\n" }), 1 }), 
		    }));
		
		
		errmsg = catch(apps[val[2]]->call(cb, val[3..<1]); publish);
		if(errmsg)
		    funcall(callback,
			explode(save_value(({RPC_FAIL, val[1], errmsg[1..<2]})),"\n")[1]);
	    }
	    else
		funcall(callback,
		    explode(save_value(({RPC_ANSWER, val[1], 0})),"\n")[1]);
	    break;
    }
}

private void handle_msg(string msg, mixed port, closure callback)
{
    state[port, S_TIME] = time();

    switch(msg[0])
    {
	case 'F': // Volle Meldung
	    state[port, S_MSG] = 0;
	    exec_msg(msg[1..<1], callback);
	    break;
	    
	case 'S': // Start
	    state[port, S_MSG] = msg[1..<1];
	    break;
	    
	case 'M': // Mitte
	    if(stringp(state[port, S_MSG]))
		state[port, S_MSG] += msg[1..<1];
	    break;
	
	case 'E': // Ende
	    if(stringp(state[port, S_MSG]))
	    {
		string val = state[port, S_MSG] + msg[1..<1];
		state[port, S_MSG] = 0;
		exec_msg(val, callback);
	    }
	    break;
    }
}

private void send_udp(string msg, int port)
{
    if(sizeof(msg)+4 <= UDPPACKETSIZE)
	efun::send_udp("127.0.0.1", port, "RPCF" + msg);
    else
    {
	efun::send_udp("127.0.0.1", port, "RPCS" + msg[0..UDPPACKETSIZE-5]);
        msg = msg[UDPPACKETSIZE-4..<1];
	while(sizeof(msg)+4>UDPPACKETSIZE)
	{
	    efun::send_udp("127.0.0.1", port, "RPCM" + msg[0..UDPPACKETSIZE-5]);
	    msg = msg[UDPPACKETSIZE-4..<1];
	}
        efun::send_udp("127.0.0.1", port, "RPCE" + msg);
    }
}

void receive_udp(string host, string msg, int port)
{
    if(member(({"127.0.0.1", "::1", "::ffff:127.0.0.1"}), host) < 0 || object_name(previous_object())!=__MASTER_OBJECT__)
	return;

    handle_msg(msg[3..<2], port, lambda(({'msg}),({#'send_udp,'msg, port})));
}

void receive_tcp(string msg)
{
    object ob = previous_object();
    if(load_name(ob) != RPC_CONNECTION)
	return;

    handle_msg(msg, ob, lambda(({'msg}), ({#'call_other, ob, "send_tcp", 'msg})));
}

protected void reset()
{
    state = filter(state, (: $2[S_TIME] > $3 :), time()-10);
    requests = filter(requests, (: $2[REQ_STARTTIME] > $3 :), time()-3600); // One hour at most.
}

void daemon_call(closure cb, closure onerr, string app, string func, varargs mixed* args)
{
    string id;
    
    if(extern_call() && strstr(object_name(previous_object()),"/secure/rpc/"))
	return;
    
    if(!daemon)
    {
#ifndef TestMUD
	do_my_error("RPC: No daemon registered.\n");
#endif
	return;
    }
    
    id = get_unique_string();
    daemon->send_tcp(explode(save_value(({RPC_REQUEST, 
	id, app, func }) + args),"\n")[1]);
    m_add(requests, id, cb, onerr, time());
}

int remove()
{
    if(daemon)
	destruct(daemon);
    destruct(this_object());
}
