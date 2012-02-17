#!/usr/bin/python
# -*- coding: utf-8 -*-

from __future__ import with_statement
import os, sys, time, re, subprocess
import email, email.Header, email.Utils, email.Message
from utils import konvert_umlaute
from picklerpc import client

SOCKETNAME = "/MUD/rpc/fifo"
HOSTNAMES  = frozenset([
                 "mine.mud.de",
             ])

def decode_header(txt):
    if txt is None:
        return None

    return " ".join([unicode(text, charset or "iso8859-15")
                     for text, charset in email.Header.decode_header(txt)])

def filter_spam(user):
    # Should we check user's mail for spam?
    return True

def strip_localhost(addr):
    parts = addr.split('@')
    if len(parts)>2:
        raise RuntimeError("Illegal address '%s'!" % (addr))
    elif len(parts)==2 and parts[1].lower() in HOSTNAMES:
        return parts[0]
    else:
        return addr

def process_mail():
    if not 'LOCAL_PART' in os.environ:
        raise RuntimeError('LOCAL_PART environment variable missing.')

    if not 'SENDER' in os.environ:
        raise RuntimeError('SENDER environment variable missing.')

    recipient = os.environ['LOCAL_PART']
    sender = os.environ['SENDER']

    if filter_spam(recipient.lower()):
        # Check for Spam...
        spamass = subprocess.Popen('/usr/bin/spamassassin -e -p /etc/spamassassin.conf',
            stdout = subprocess.PIPE,
            shell = True, close_fds = True)
        msg = email.message_from_file(spamass.stdout)

        if msg.get('X-Spam-Flag','').lower() == 'yes':
            raise RuntimeError('Your mail was detected as SPAM.')
    else:
        msg = email.message_from_file(sys.stdin)

    author = decode_header(msg['From'])
    if author is None:
        raise RuntimeError('No FROM address given.')

    cc = email.utils.getaddresses(msg.get_all('To', []) + msg.get_all('Cc', []))

    date = decode_header(msg['Date'])
    if not date is None:
        date = email.Utils.parsedate_tz(date)

    if date is None:
        date = time.time()
    else:
        date = email.Utils.mktime_tz(date)

    header = msg.items()
    if msg.is_multipart():
        text = None
        for part in msg.get_payload():
            if part.get_content_type() == 'text/plain':
                text = part.get_payload(None, True)
                cs = part.get_content_charset()

                # Replace header entries with the ones from the payload
                plheader = part.items()
                plheaderentries = set([entry[0] for entry in plheader])
                header = [ entry for entry in header if not entry[0] in plheaderentries ] + plheader

                break
        if text is None:
            raise RuntimeError('No plain text part found. HTML only mails are not accepted.')
    else:
        text = msg.get_payload(None, True)
        cs = msg.get_content_charset()

    subj = konvert_umlaute(decode_header(msg['Subject'] or ''))
    text = konvert_umlaute(unicode(text,cs or "iso8859-15"))

    author_addr = email.Utils.parseaddr(author)
    addtext = konvert_umlaute(sender) + ":\n" + konvert_umlaute(author) + "\n"
    if msg['Reply-To']:
        addtext += konvert_umlaute(decode_header(msg['Reply-To'])) + "\n"

    mudmail = client.synconnect(SOCKETNAME, "mail")
    mudmail.receivemail(recipient, strip_localhost(author_addr[1]),
        [ strip_localhost(addr[1]) for addr in cc ],
        subj, date, addtext + "\n" + text, header)
    mudmail._close()

try:
    process_mail()
except BaseException, ex:
    sys.exit(str(ex))
