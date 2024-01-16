from .templates import BasicTemplate

from multiprocessing import Pipe


class Basic(BasicTemplate):
    SERV_TYPE = "Basic"
    SERV_INFO = "Basic Server for test Basic Server for test Basic Server for test Basic Server for test Basic Server for test Basic Server for test Basic Server for test"
    def __init__(self, ctrl_pipe: Pipe, conf : dict = {}):
        super().__init__(ctrl_pipe=ctrl_pipe, conf=conf)
        