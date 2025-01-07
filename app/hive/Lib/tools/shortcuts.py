import os


class Shortcuts:
    def __init__(self, queen: object):
        self.queen = queen
        self.dir_main = self.queen.conf.dir_main
        self.dir_shortcuts = self.queen.conf.dir_shortcuts
        self.dir_lib = self.queen.dir_lib
        self.shortcuts = {
            "icons" : os.path.join(self.dir_lib, "icons"),
            "my_payload" : os.path.join(self.dir_lib, "items", "payloads", "my_payload.data"),
            "sherlock_files" : os.path.join(self.dir_lib, "items", "food", "sherlock_files.data")
        }
    

    def make_shortcuts(self) -> None:
        for name, path in self.shortcuts.items():
            lname = os.path.join(self.dir_shortcuts, name)
            if os.path.exists(lname):
                continue
            os.symlink(path, lname)
