# -*- coding: utf-8 -*-

UMLAUTE = {
    u'Ä': 'Ae',
    u'Ö': 'Oe',
    u'Ü': 'Ue',
    u'ä': 'ae',
    u'ö': 'oe',
    u'ü': 'ue',
    u'ß': 'ss',
    u'€': 'EUR',
    u'\xa0': ' ', # Non-breaking space
    }

def konvert_umlaute(txt):
    res = ''
    for ch in txt:
        if ch in UMLAUTE:
            res += UMLAUTE[ch]
        elif ord(ch)<128:
            res += ch
    return res
