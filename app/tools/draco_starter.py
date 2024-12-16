import argparse


class DracoStarter:
    def __init__(self):
        self.parser = argparse.ArgumentParser("Draconus", description="Draconus Help:", add_help=True)
        self.add_args()
    
    def add_args(self) -> None:
        self.parser.add_argument("-c", "--config", help="Path to extra config file", required=False)
        self.parser.add_argument("-f", "--force", required=False, action="store_true", help="Force to run Draconus")
        self.parser.add_argument("-b", "--background", required=False, action="store_true")
    
    def make_config(self) -> dict:
        conf = {}
        conf["EXTRA_CONFIG"] = self.args.config
        conf["FORCE_RUN"] = self.args.force
        conf["RUN_BACK"] = self.args.background
        return conf
    
    def output(self) -> dict:
        self.args = self.parser.parse_args()
        conf = self.make_config()
        return conf




