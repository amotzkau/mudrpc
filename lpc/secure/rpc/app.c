// ----------------------------------------------------------------
// File:        /secure/rpc/app.c
// Description: RPC functions
// Author:      Gnomi
//

private functions inherit "/secure/i/password";

#include <apps.h>
#include <config.h>
#include <finger.h>
#include <level.h>
#include <rpc.h>

int level;
string real_name;

private void clear_vars()
{
    "*"::clear_vars();
    level = 0;
}

private int load_player(string name)
{
    if(real_name == name)
	return 1;

    clear_vars();
    if(!restore_object(PLAYER_FILE(name)))
	return 0;

    return 1;
}

static mixed password(string name, string pass, string whatfor)
{
    string res;
    
    if(!load_player(name))
	return 0;

    res = check_password(pass, name, 0);
    if(res)
	return res;

    switch(whatfor)
    {
	case "ftp":
	    if(level<LVL_WIZ)
		return 0;
    }

    return level;
}

void call(closure cb, mixed* args)
{
    if(object_name(previous_object()) != RPC_SERVER)
	return;
    
    funcall(cb, apply(#'call_other, this_object(), args));
}
