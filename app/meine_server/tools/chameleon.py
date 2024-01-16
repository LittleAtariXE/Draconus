import base64

class Chameleon:
    def __init__(self, format_code):
        self.format = format_code
    
    def encrypt(self, msg):
        msg = str(msg).encode(self.format)
        return base64.b64encode(msg)
    
    def decrypt(self, msg):
        msg = base64.b64decode(msg)
        return msg.decode(self.format)