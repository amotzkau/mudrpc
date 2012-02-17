#!/usr/bin/python
# -*- coding: utf-8 -*-
import email, email.Utils, email.Message
import smtplib
import rpctools

class InternalMail(rpctools.CallbackHelper):
    " This is the mail application that should be called from the MUD. "
    def __init__(self):
        pass

    def sendmail(self, envelop_from, envelop_to, header, date, ref, text):
        """Sends an email to the outside world.

        envelop_from, envelop_to denote the real sender and recipient
        given to the MTA (via SMTP to localhost).

        header can be either a dict, list of pairs or plain string.

        date is a unix date (seconds since 1970).

        ref can be a list of referenced message ids.

        text is the message in plain ascii.
        """

        header_dict = header_text = header_list = None
        if header:
            if hasattr(header, 'iteritems'):
                header_dict = header
            elif hasattr(header, 'encode'):
                header_text = header
            else:
                header_list = header

        if header_text:
            msg = email.message_from_string(header_text)
        else:
            msg = email.Message.Message()

        if header_dict:
            for key,val in header_dict.iteritems():
                msg.add_header(key, val)

        if header_list:
            for key,val in header_list:
                msg.add_header(key, val)

        if date:
            msg['Date'] = email.Utils.formatdate(date, True)

        if not 'Organization' in msg:
            msg['Organization'] = 'MUD post office'
        if not 'User-Agent' in msg:
            msg['User-Agent'] = 'MUD-Mail/1.0'
        if not 'Message-Id' in msg:
            msg['Message-Id'] = email.Utils.make_msgid("mudmail")
        if ref and len(ref):
            msg['References'] = " ".join(ref)
        if not 'Lines' in msg:
            msg['Lines'] = str(text.count("\n"))
        msg.set_payload(text, 'ascii')

        mta = smtplib.SMTP('127.0.0.1')
        mta.sendmail(envelop_from, [envelop_to], msg.as_string())
        mta.quit()
