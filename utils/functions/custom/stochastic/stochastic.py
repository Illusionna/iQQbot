import os
import re
import time
import ctypes
import random
import requests
from ....tools.inherit import Function, Run
from ....tools.send import send_message


class GenerateFloatNumber(Function, Run):
    invoke = '/num'
    permission = 1
    description = '/num 2.71828 3.1415'

    def __init__(self, params: dict, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        super().__auto__(self, **locals())
        self.run()

    @Run.authorize()
    def run(self) -> None:
        data = self.params['data']
        raw_message: str = data.get('raw_message')
        text = raw_message.replace(f'{GenerateFloatNumber.invoke} ', '', 1)
        if text == GenerateFloatNumber.invoke:
            send_message(str(random.random()), self.params['config']['socket'], data)
        else:
            L = text.split()
            if (len(L) == 2) and all(bool(re.match(r'^-?(\d+(\.\d*)?|\.\d+)([eE][+-]?\d+)?$', i)) for i in L):
                lib_path = os.path.join(os.getcwd(), 'utils', 'functions', 'custom', 'stochastic', 'random.dll')
                lib = ctypes.CDLL(lib_path)
                lib.Srand48.argtypes = [ctypes.c_uint]
                lib.Srand48.restype = None
                lib.GenerateRandom.argtypes = [ctypes.c_double, ctypes.c_double]
                lib.GenerateRandom.restype = ctypes.c_double
                lib.Srand48(int(time.time()))
                send_message(f'{lib.GenerateRandom(float(L[0]), float(L[1]))}', self.params['config']['socket'], data)
            else:
                send_message(f'格式应为 {GenerateFloatNumber.invoke} 12e3 7.2', self.params['config']['socket'], data)


class Sample(Function, Run):
    invoke = '/抽样'
    permission = 1
    description = '使用 "/抽样 5" 即可'

    def __init__(self, params: dict, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        super().__auto__(self, **locals())
        self.run()

    @Run.authorize()
    def run(self) -> None:
        data = self.params['data']
        group_id: int | None = data.get('group_id')
        raw_message: str = data.get('raw_message')
        text = raw_message.replace(f'{Sample.invoke} ', '', 1)
        if text != Sample.invoke:
            L = text.split()
            if len(L) == 1:
                try:
                    n = int(L[0])
                    if group_id:
                        url = f"http://{self.params['config']['socket']}/get_group_member_list"
                        json = requests.post(url, json = {'group_id': group_id}, timeout=5).json().get('data')
                        if 0 <= n <= len(json):
                            docs = '随机抽取以下群友\n  '
                            s = set()
                            ans = random.sample(json, n)
                            for i in ans:
                                s.add(f"- [CQ:at,qq={i['user_id']}] ({i['user_id']})")
                            send_message(docs + '\n  '.join(s), self.params['config']['socket'], data)
                except:
                    pass