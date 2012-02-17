#!/usr/bin/python
import os
import time
import email, email.Header, email.Utils, email.Message
import rpctools
from utils import konvert_umlaute

VALID_NGS = { "de.alt.mud": True }

def decode_header(txt):
    if txt is None:
        return None

    return " ".join([unicode(text, charset or "iso8859-15")
                     for text, charset in email.Header.decode_header(txt)])

class ExternalNews:
    " Applikation fuer INN "
    def __init__(self, mudnews):
        self.mudnews = mudnews

    def importnews(self, cb, token):
        msgproc = os.popen2(['/usr/lib/news/bin/sm', token ], 'rt') 
        msgproc[0].close()
        msg = email.message_from_file(msgproc[1])
        msgproc[1].close()

        author = decode_header(msg['From'])
        if author is None:
            cb(True, None)
            return

        author = email.Utils.parseaddr(author)

        ngs = [ng.strip() for ng in msg['Newsgroups'].split(',')]
        ngs = [ng for ng in ngs if ng in VALID_NGS or ng.startswith("mud.") ]

        if len(ngs)==0:
            cb(True, None)
            return

        subj = decode_header(msg['Subject'] or '')
        mid = msg['Message-ID']

        ref = msg['References'] or ''
        ref = ref.replace("\n","").replace("\t"," ")
        ref = [msgid.strip() for msgid in ref.split(' ')]
        ref = [msgid for msgid in ref if len(msgid)>1]

        date = decode_header(msg['Date'])
        if not date is None:
            date = email.Utils.parsedate_tz(date)

        if date is None:
            date = time.time()
        else:
            date = email.Utils.mktime_tz(date)

        if msg.is_multipart():
            text = None
            for part in msg.get_payload():
                if part.get_content_type() == 'text/plain':
                    text = part.get_payload(None, True)
                    cs = part.get_content_charset()
                    break
            if text is None:
                cb(True, None)
                return
        else:
            text = msg.get_payload(None, True)
            cs = msg.get_content_charset()

        subj = konvert_umlaute(subj)
        addr = author[1]
        author = konvert_umlaute(author[0] or author[1])
        text = konvert_umlaute(unicode(text,cs or "iso8859-15"))

        self.mudnews.importnews(cb, ngs, author, subj, int(date), mid, ref, text)

    def cancelnews(self, cb, token):
        msgproc = os.popen2(['/usr/lib/news/bin/sm', token ], 'rt') 
        msgproc[0].close()
        msg = email.message_from_file(msgproc[1])
        msgproc[1].close()

        author = decode_header(msg['From'])
        cmd = decode_header(msg['Control'])
        if author is None or cmd is None:
            cb(True, None)
            return

        author = email.Utils.parseaddr(author)
        cmd = cmd.split(" ",1)
        if len(cmd)<2:
            cb(True, None)
            return

        if cmd[0].lower() != "cancel":
            cb(True, None)
            return

        ngs = [ng.strip() for ng in msg['Newsgroups'].split(',')]
        ngs = [ng for ng in ngs if ng in VALID_NGS or ng.startswith("mud.") ]

        if len(ngs)==0:
            cb(True, None)
            return

        author = konvert_umlaute(author[0] or author[1])
        self.mudnews.cancelnews(cb, ngs, author, cmd[1])

class InternalNews(rpctools.CallbackHelper):
    def __init__(self):
        pass

    def exportnews(self, usenet, autor, addr, subject, date, mid, ref, text):
        msgproc = os.popen2(['/usr/bin/rnews' ], 'wt') 
        msgproc[1].close()

        msg = email.Message.Message()
        msg["Path"] = "mud-news"
        msg["Newsgroups"] = usenet

        if usenet.startswith("mud."):
            name = autor
        else:
            name = autor+"@MUD"

        fulladdr = email.Utils.parseaddr(addr)
        msg["From"] = email.Utils.formataddr(( len(fulladdr[0]) and fulladdr[0] or name, len(fulladdr[1]) and fulladdr[1] or addr ))
        msg['Subject'] = subject
        msg['Date'] = email.Utils.formatdate(date, True)
        msg['Organization'] = 'MUD post office'
        msg['Lines'] = str(text.count("\n"))
        msg['Message-Id'] = mid
        if ref and len(ref):
            msg['References'] = " ".join(ref)

        msg['X-Muduser'] = autor
        msg['X-Mud'] = 'MUD'
        msg['X-Complaints-To'] = 'usenet@mine.mud.de'
        msg['User-Agent'] = 'MUD-Usenet-Gateway/1.0'
        msg.set_payload(text, 'ascii')

        msgproc[0].write(msg.as_string(False))
        msgproc[0].close()

    def deletenews(self,mid):
        os.spawnl(os.P_WAIT, "/usr/sbin/ctlinnd","ctlinnd","cancel", mid);
