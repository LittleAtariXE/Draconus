import base64


class Chameleon:
    def __init__(self, format_code: str):
        self.format_code = format_code

    
    def encrypt(self, text: str) -> bytes:
        text = text.encode(self.format_code)
        return base64.b64encode(text)
    
    def decrypt(self, text: bytes) -> str:
        text = base64.b64decode(text)
        return text.decode(self.format_code)
        