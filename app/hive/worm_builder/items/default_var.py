class Default:
    def __init__(self, builder: object):
        self.conf = builder
    
    @property
    def var(self) -> dict:
        var = {
            "PAYLOAD" : "pass",
            "MODULES" : {},
            "IP_ADDR" : self.conf.ip,
            "TCP_SOCK_TO" : self.conf.tcp_sock_to_recive,
            "TCP_SOCK_SEPARATOR" : self.conf.tcp_socket_separator,
            "RAW_LEN" : self.conf.tcp_socket_raw_len,
            "FORMAT_CODE" : self.conf.tcp_socket_format
        }

        return var
    
    