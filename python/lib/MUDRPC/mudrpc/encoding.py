import ply.lex as lex
import ply.yacc as yacc
import StringIO

class Parser:
    tokens = (
        'ARRAY_BEGIN', 'ARRAY_END', 'MAPPING_BEGIN', 'MAPPING_END',
        'NUMBER', 'STRING'
    )

    literals = ":;.,<>="

    t_ARRAY_BEGIN = r'\(\{'
    t_ARRAY_END = r'\}\)'
    t_MAPPING_BEGIN = r'\(\['
    t_MAPPING_END = r'\]\)'
#    t_IDENTIFIER = r'[A-Za-z_]\w*'

    def t_NUMBER(self, t):
        r'-?\d+'
        t.value = int(t.value)
        return t

    def t_STRING(self, t):
        r'"([^\\"]+|\\.)*"'
        #t.value=t.value[1:-1].decode("string-escape")
        t.value=self.unescapestring(t.value[1:-1])
        return t

    t_ignore = ' \t\n'

    def t_error(self, t):
        print "Illegal character '%s'" % t.value[0]
        t.lexer.skip(1)

    def p_pointer_def(self, p):
        '''value : '<' NUMBER '>' '=' value'''
        self.pointer[p[2]] = p[5]
        p[0] = p[5]

    def p_pointer_ref(self, p):
        "value : '<' NUMBER '>'"
        p[0] = self.pointer[p[2]]

    def p_string_value(self, p):
        'value : STRING'
        p[0] = p[1]

    def p_integer_value(self, p):
        'value : NUMBER'
        p[0] = p[1]

    def p_array_value(self, p):
        'value : ARRAY_BEGIN elements ARRAY_END'
        p[0] = p[2]

    def p_empty_elements(self, p):
        "elements :"
        p[0] = []

    def p_more_elements(self, p):
        "elements : elements value ','"
        p[0] = p[1]+[p[2]]

    def p_empty_mapping_value(self, p):
        '''value : MAPPING_BEGIN ':' NUMBER MAPPING_END'''
        p[0] = {}

    def p_mapping_value(self, p):
        'value : MAPPING_BEGIN mapkeys MAPPING_END'
        p[0] = p[2]

    def p_empty_map_keys(self, p):
        'mapkeys :'
        p[0] = {}

    def p_more_map_keys(self, p):
        "mapkeys : mapkeys value mapvalues ','"
        p[0] = p[1].copy()
        p[0][p[2]] = p[3]

    def p_map_values(self, p):
        '''mapvalues : ':' moremapvalues value'''
        p[0] = p[2]+[p[3]]
        if len(p[0])==1:
            p[0] = p[0][0]

    def p_no_map_values(self, p):
        'mapvalues :'
        p[0] = None

    def p_more_map_values(self, p):
        "moremapvalues : moremapvalues value ';'"
        p[0] = p[1]+[p[2]]

    def p_no_more_map_values(self, p):
        "moremapvalues :"
        p[0] = []

    def p_error(self, p):
        print "Syntax error!"

    def __init__(self):
        self.lexer = lex.lex(module=self)
        self.yacc = yacc.yacc(module=self,debug=1)

    def parse(self, text):
        self.pointer = {}
        return self.yacc.parse(text)

    escape = {
        r'0': '\0',
        r'a': '\a',
        r'b': '\b',
        r't': '\t',
        r'n': '\n',
        r'v': '\v',
        r'f': '\f',
        r'r': '\r',
    }

    def unescapestring(self,text):
        src = text
        dest = ""
        try:
            while True:
                i = src.index('\\')
                dest += src[0:i]
                if src[i+1] in self.escape:
                    dest += self.escape[src[i+1]]
                else:
                    dest += src[i+1]
                src = src[i+2:]
        except ValueError:
            pass

        return dest+src

class Generator:
    escape = {
        '\0': r'\0',
        '\a': r'\a',
        '\b': r'\b',
        '\t': r'\t',
        '\n': r'\n',
        '\v': r'\v',
        '\f': r'\f',
        '\r': r'\r',
        '\"': r'\"'
    }

    def unescapestring(self,text):
        s = text.replace('\\',r'\\')
        for key, val in self.escape.iteritems():
            s = s.replace(key, val)
        return s

    def write(self, buf, value):
        if hasattr(value, "keys"):
            self.writemap(buf, value)
        elif hasattr(value, "encode"):
            self.writestr(buf, value)
        elif hasattr(value, "__iter__"):
            self.writearr(buf, value)
        elif hasattr(value, "__int__"):
            self.writeint(buf, value)
        elif value == None:
            self.writeint(buf, 0)
        else:
            self.writeerr(buf)

    def writemap(self, buf, value):
        buf.write('([')
        hasvalues = False
        for val in value.itervalues():
            if val != None:
                hasvalues = True
                break

        for key,val in value.iteritems():
            self.write(buf, key)
            if hasvalues:
                buf.write(':')
                self.write(buf, val)
            buf.write(',')
        buf.write('])')

    def writearr(self, buf, value):
        buf.write('({')
        for val in value:
            self.write(buf, val)
            buf.write(',')
        buf.write('})')

    def writestr(self, buf, value):
        buf.write('"%s"' % self.unescapestring(value.encode('utf8')))

    def writeint(self, buf, value):
        buf.write('%d' % value)

    def writeerr(self, buf):
        buf.write("<error>")

    def build(self, value):
        buf = StringIO.StringIO()
        self.write(buf, value)
        return buf.getvalue()

scan = Parser()
gen = Generator()

class LPCEncoding:
    def __init__(self):
        pass

    def encode(self, data):
        return gen.build(data)

    def decode(self, data):
        return scan.parse(data)
