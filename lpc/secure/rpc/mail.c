// ----------------------------------------------------------------
// File:        /secure/rpc/mail.c
// Description: RPC functions for the e-mail gateway
// Author:      Gnomi

#include <rpc.h>

static void receivemail(string player, string from_addr, string* cc,
    string subject, int date, string text, mixed* header)
{
    /* Receive the e-mail for 'player' (mixed case, so use lower_case())
     * from 'from_addr' and going also to 'cc' (if both come from
     * local users the hostpart is striped). The message's header
     * are in 'header' which is an array of pairs of the header name
     * and value.
     */
}

void call(closure cb, mixed* args)
{
    if(object_name(previous_object()) != RPC_SERVER)
        return;

    funcall(cb, apply(#'call_other, this_object(), args));
}

void sendmail(string sender, string recipient, mixed header, int date, string* references, string text)
{
    /* sender and recipient denote the real (envelope) sender and recipient.
     * However there should be 'To', 'From' and 'Cc' entries in the header.
     * 'header' may be a string, array of strings or a mapping.
     * 'references' can be an array of referenced message ids.
     * 'text' is the message in plain ascii.
     */

    RPC_SERVER->daemon_call(
        function void()
        {
            // On success
            printf("Sent mail to %s.", recipient);
        },
        function void(string error)
        {
            // On Error
            printf("Error sending mail to %s: %s\n", recipient, error);
        },
        "mail", "sendmail", // application and function
        sender, recipient, header, date, references, text);
}
