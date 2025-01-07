import os

from configparser import ConfigParser


class Builder:
    def __init__(self, extra_config_path: str = None):
        self.extra_config_path = extra_config_path
        self.dir_main = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
        self.default_config = os.path.join(self.dir_main, "CONFIG.ini")
        self.dir_system_file = os.path.join(self.dir_main, "app", "_sys_files")
        self.socket_draco_msg = os.path.join(self.dir_system_file, "draco.msg")
        self.socket_draco_ctrl = os.path.join(self.dir_system_file, "draco.ctrl")
        self.draco_lock_file = os.path.join(self.dir_system_file, "draconus.lock")
        self.dir_output = os.path.join(self.dir_main, "OUTPUT")
        self.dir_logs = os.path.join(self.dir_output, "Logs")
        self.dir_hive_out = os.path.join(self.dir_output, "Hive")
        self.dir_library_items = os.path.join(self.dir_hive_out, "Lib", "items")
        self.dir_shortcuts = os.path.join(self.dir_output, "Shortcuts")
        self.dir_in = os.path.join(self.dir_main, "IN")
        self.read_config()
        self.make_dirs()

    
    def _show_config(self) -> dict:
        conf = {}
        for k, i in self.__dict__.items():
            if k.startswith("_"):
                continue
            if k == "unix_socket_separator":
                continue
            conf[k] = i
        return conf
    
    @property
    def CONF(self) -> dict:
        return self._show_config()

    
    def read_config(self):
        config = ConfigParser()
        config.read(self.default_config)
        conf = config["CONFIG"]
        dev = config["DEV"]
        if self.extra_config_path:
            extra = ConfigParser()
            extra.read(self.extra_config_path)
            extra_conf = extra["CONFIG"]
            extra_dev = extra["DEV"]
            conf.update(extra_conf)
            dev.update(extra_dev)
        
        main = {
            "ip" : conf.get("ip"),
            "unix_socket_raw_len" : int(conf.get("unix_socket_raw_len")),
            "unix_socket_format" : conf.get("unix_socket_format"),
            "tcp_socket_format" : conf.get("tcp_socket_format"),
            "tcp_socket_raw_len" : int(conf.get("tcp_socket_raw_len")),
            "vanilla_print" : conf.getboolean("vanilla_print"),
            "show_no_important_messages" : conf.getboolean("show_no_important_messages"),
            "task_pause_clean" : float(dev.get("task_pause_clean")),
            "unix_socket_separator" : conf.get("unix_socket_separator"),
            "tcp_socket_separator" : conf.get("tcp_socket_separator"),
            "dev_msg" : dev.getboolean("dev_msg"),
            "tcp_sock_to_listening" : int(dev.get("tcp_socket_timeout_listening")),
            "unix_sock_to_recive" : int(dev.get("unix_socket_timeout_recive")),
            "tcp_sock_to_recive" : int(dev.get("tcp_socket_timeout_recive")),
            "central_clean_pause" : int(dev.get("central_cleaner_time_pause")),
            "sender_socket_to" : 60,
            "dlc_name" : conf.get("DLC_FILE_NAME"),
            "tcp_raw_buffer_to" : int(conf.get("TCP_RAW_BUFFER_TIMEOUT")),
            "payload_default_encode" : conf.get("PAYLOAD_DEFAULT_ENCODE")
        }
        self.update_builder(main)
        
    
    def update_builder(self, config: object) -> None:
        for k, i in config.items():
            setattr(self, k, i)
    
    def make_dirs(self) -> None:
        if not os.path.exists(self.dir_system_file):
            os.mkdir(self.dir_system_file)
        if not os.path.exists(self.dir_output):
            os.mkdir(self.dir_output)
        if not os.path.exists(self.dir_logs):
            os.mkdir(self.dir_logs)
        if not os.path.exists(self.dir_hive_out):
            os.mkdir(self.dir_hive_out)
        if not os.path.exists(self.dir_shortcuts):
            os.mkdir(self.dir_shortcuts)
        if not os.path.exists(self.dir_in):
            os.mkdir(self.dir_in)

        



  






