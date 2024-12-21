import os
import requests
from ...tools.inherit import Function, Run
from ...tools.send import send_message
from ...tools.read import read_json


class Privilege(Function, Run):
    invoke = '/特权者'
    permission = 2

    def __init__(self, params: dict, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        super().__auto__(self, **locals())
        self.run()

    @Run.authorize()
    def run(self) -> None:
        data: dict = self.params['data']
        raw_message: str = data.get('raw_message')
        if raw_message == Privilege.invoke:
            json = read_json(os.path.join('configs', 'privilege.json'))
            if json:
                s = set()
                for key, value in json.items():
                    if len(value) != 0:
                        url = f"http://{self.params['config']['socket']}"
                        url = url + '/get_stranger_info'
                        ans = requests.post(url, {'user_id': int(key)}, timeout=5).json().get('data')
                        if ans:
                            tmp = '\n'.join(f'    - {item}' for item in value)
                            s.add(f"{ans.get('nickname')} ({key})\n{tmp}")
                send_message('\n'.join(s), self.params['config']['socket'], data)
            else:
                send_message('空名单', self.params['config']['socket'], data)