// ----------------------------------------------------------------
// File:        /secure/rpc/ftpd.c
// Description: RPC functions for the ftpd
// Author:      Gnomi
//

#include <rpc.h>
#include <config.h>
#include <files.h>

/* perm:
        Read permissions:
         - "e" = change directory (CWD command)
         - "l" = list files (LIST, NLST, STAT, MLSD, MLST commands)
         - "r" = retrieve file from the server (RETR command)

        Write permissions:
         - "a" = append data to an existing file (AxPPE command)
         - "d" = delete file (DELE command)
         - "f" = rename file or directory from (RNFR command)
         - "t" = rename file or directory to (RNTO command)
         - "m" = create directory (MKD command)
         - "n" = delete directory (RMD command)
*/
static int check_permission(string wiz, string perm, string path)
{
    int idx;

    debug_message(sprintf("%s(%s): %s\n", wiz, perm, path), 14);

    if(member("el", perm[0]) >= 0)
    {
        if(path[<1] == '/')
            path += "*";
        else if(file_size(path) == FSIZE_DIR)
            path += "/*";
        return MASTER_OB->valid_read(path, wiz, "get_dir", 0);
    }
    else if(perm == "r")
        return MASTER_OB->valid_read(path, wiz, "read_file", 0);
    else if((idx=member("wadftmn", perm[0])) >= 0)
        return MASTER_OB->valid_write(path, wiz, ({"write_file", "write_file", "remove_file", "rename_from", "rename_to", "mkdir", "rmdir"})[idx], 0);
    else
        return 0;
}

void call(closure cb, mixed* args)
{
    if(object_name(previous_object()) != RPC_SERVER)
	return;
    
    funcall(cb, apply(#'call_other, this_object(), args));
}
