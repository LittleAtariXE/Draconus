import string
import base64
from random import choice, randint
from typing import Union

class DigDug:
    def __init__(self):
        self.raw_table, self.rev_raw_table = self._make_raw_table()
        self.table = None
    
    def _make_raw_table(self) -> tuple[dict, dict]:
        chars = []
        table = {}
        rev_table = {}
        for c in string.ascii_letters + string.digits + string.punctuation:
            chars.append(c)
        for c in [" ", "\n", "\t"]:
            chars.append(c)
        count = 0
        while len(chars) > 0:
            c = choice(chars)
            chars.remove(c)
            if count < 10:
                num = f"0{count}"
            else:
                num = str(count)
            table[num] = c
            rev_table[c] = num
            count += 1

        return (table, rev_table)
    
    def _make_simple_key(self, key_len: int, key_postion: int, key: str) -> str:
        new_key = ""
        while len(new_key) < key_len + 2:
            if len(new_key) == key_postion:
                new_key += key
                continue
            new_key += str(randint(0, 9))
        return new_key
    
    def _morph_table(self, key_len: int = 1) -> tuple[dict, int]:
        key_postion = randint(0, key_len)
        _table = {}
        for k, i in self.raw_table.items():
            new_key = self._make_simple_key(key_len, key_postion, k)
            _table[new_key] = i
        table = {}
        while len(_table) > 0:
            _tmp = []
            for k in _table.keys():
                _tmp.append(k)
            key = choice(_tmp)
            table[key] = _table[key]
            del _table[key]
        return (table, key_postion)

    def _gen_string(self, length: int = 10) -> str:
        chars = string.ascii_letters
        text = ""
        while len(text) < length:
            c = chars[randint(0, len(chars) - 1)]
            text += c
        return text
    
    def _gen_master_key(self, key_postion: int, randomize_element: int = 3, randomize_data: int = 3) -> str:
        data = []
        rd_max = int(randomize_data * 2.5)
        for _ in range(randomize_element):
            part = []
            for _ in range(randint(randomize_data, rd_max)):
                part.append(self._gen_string(randint(randomize_data, rd_max)))
            data.append(part)
        code = ""
        data_sum = 0
        count = 0
        for d in data:
            data_sum += len(d)
            if count == randomize_element - 1:
                code += f"len({d})"
            else:
                code += f"len({d}) + "
            count += 1
        key_diff = data_sum - key_postion
        last = []
        for _ in range(key_diff):
            last.append(self._gen_string(randint(randomize_data, rd_max)))
        code += f' - len({last})\n'
        return code
    
    def _make_real_table(self, master_key_var_name: str, table_var: str, real_table_var_name: str) -> str:
        empty = {}
        code = f"""\n{real_table_var_name} = {empty}\n
for k, i in {table_var}.items():
    {real_table_var_name}[k[{master_key_var_name}:{master_key_var_name}+2]] = i
\n"""
        return code
    

    def _make_loader_real_table(self, code: str, launcher_var_name: str, count: int = 1) -> str:
        fcount = int(count * 8)
        code = code.encode('utf-8')
        for _ in range(count):
            code = base64.b64encode(code)
        fake_count_var = self._gen_string(fcount)
        fake_count_value = self._gen_string(fcount)
        count_var = self._gen_string(fcount)
        count_value = self._gen_string(fcount - count)
        lcode = f"""\n{fake_count_var} = '{fake_count_value}'\n{count_var} = '{count_value}'\n{launcher_var_name} = {code}\nfor _ in range(len({fake_count_var}) - len({count_var})):
    {launcher_var_name} = base64.b64decode({launcher_var_name})
exec({launcher_var_name})\n"""
        lcode = base64.b64encode(lcode.encode("utf-8"))
        lcode = f"""exec("exec(base64.b64decode({lcode}))")\n"""
        return lcode
    
    def _make_code_builder(self, code_var: str, real_table_var: str, real_code: str) -> str:
        code = f"""\n{real_code} = ""\nfor c in {code_var}:
    {real_code} += {real_table_var}[c]
exec({real_code})\n"""
        code = base64.b64encode(code.encode('utf-8'))
        code = f'exec("exec(base64.b64decode({code}))")\n'
        return code
    
    def shadow(self, code: str, var: dict) -> str:
        base_len = var["Dig_var_len"]
        base_max_len = int(base_len * 2.5)
        table, key_postion = self._morph_table(var["Dig_key_len"])
        obf_code = ""
        table_var = self._gen_string(randint(base_len, base_max_len))
        obf_code += f'{table_var} = {str(table)}\n'
        code_var = self._gen_string(randint(base_len, base_max_len))
        code_data = []
        for c in code:
            code_data.append(self.rev_raw_table[c])
        obf_code += f'{code_var} = {code_data}\n'
        master_key_var = self._gen_string(randint(base_len, base_max_len))
        master_key_data = self._gen_master_key(key_postion, randomize_data=base_len, randomize_element=var["Dig_mkey_rand"])
        obf_code += f'{master_key_var} = {master_key_data}\n'
        real_table_var = self._gen_string(randint(base_len, base_max_len))
        real_table = self._make_real_table(master_key_var, table_var, real_table_var)
        real_table_inside = self._gen_string(randint(base_len, base_max_len))
        real_table = self._make_loader_real_table(real_table, real_table_inside, var["Dig_run_count"])
        obf_code += real_table + "\n"
        real_code_var = self._gen_string(randint(base_len, base_max_len))
        real_code = self._make_code_builder(code_var, real_table_var, real_code_var)
        obf_code += real_code + "\n"

        return obf_code