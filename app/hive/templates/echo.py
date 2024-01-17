

class EchoClient(BasicWorm):
    def __init__(self):
        super().__init__()
        self.name = "Echo_Client"
    
    def Work(self) -> bool:
        msg = self.makeSysMsg(["e", "Hello World"])
        self.sendMsg(msg)
        response = self.reciveMsg()
        print("RESPONSE: ", response)
        return False
        