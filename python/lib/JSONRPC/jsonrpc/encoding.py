import simplejson

# Mappings duerfen nur Strings als Keys haben.

class JSONEncoding:
    def __init__(self):
        pass

    def encode(self, data):
        return simplejson.dumps(data)

    def decode(self, data):
        return simplejson.loads(data)
