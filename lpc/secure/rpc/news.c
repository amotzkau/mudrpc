// ----------------------------------------------------------------
// File:        /secure/rpc/news.c
// Description: RPC functions for the usenet gateway
// Author:      Gnomi

#include <rpc.h>

static void importnews(string* groups, string author, string subject, int date,
    string mid, string* refs, string text)
{
    /* A post into the newsgroups 'groups' from 'author' arrived.
     * 'mid' is the message id, 'refs' the list of referenced message
     * ids.
     */
}

static void cancelnews(string *gruppen, string autor, string mid)
{
    /* The post with the message id 'mid' was cancelled. */
}

static mixed* get_newsgroups(string name)
{
    /* Return a pair of lists of newsgroups.
     * The first list are the newsgroups 'name' is allowed to read,
     * the second list are the newsgroups he may post into.
     */
    return ({ ({"de.alt.mud"}), ({"de.alt.mud"}) });
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

void exportnews(string group, string sender_name, string sender_address, string subject, int date, string mid, string* references, string text)
{
    /* Post an article to 'group' from 'sender_name' <'sender_address'>.
     */

    RPC_SERVER->daemon_call(
        function void()
        {
            // On success
            printf("Posted to to %s.", group);
        },
        function void(string error)
        {
            // On Error
            printf("Error posting to %s: %s\n", group, error);
        },
        "news", "exportnews", // application and function
        group, sender_name, sender_address, subject, date, mid, references, text);
}

void deletenews(string mid)
{
    /* Cancel the post with the message id 'mid'.
     */
    RPC_SERVER->daemon_call(
        function void()
        {
            // On success
            printf("Cancelled %s.", mid);
        },
        function void(string error)
        {
            // On Error
            printf("Error cancelling %s: %s\n", mid, error);
        },
        "news", "deletenews", // application and function
        mid);
}
