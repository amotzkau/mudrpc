import pickle
import base64

if hasattr(base64,"b64encode"):
    from base64 import b64encode, b64decode
else:
    from base64 import encodestring as b64encode
    from base64 import decodestring as b64decode

class PickleEncoding:
    def __init__(self):
	pass

    def encode(self, data):
	return b64encode(pickle.dumps(data, -1))

    def decode(self, data):
	return pickle.loads(b64decode(data))
