from ...tools.inherit import Function, Run
from ...tools.send import send_message


class Echo(Function, Run):
    invoke = '/echo'
    permission = 1
    description = '/echo 一些话'

    def __init__(self, params: dict, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        super().__auto__(self, **locals())
        self.run()

    @Run.authorize()
    def run(self) -> None:
        data: dict = self.params['data']
        raw_message: str = data.get('raw_message')
        text = raw_message.replace(f'{Echo.invoke} ', '', 1)
        if (text != Echo.invoke) and (len(text) != 0):
            try:
                send_message(text, self.params['config']['socket'], data)
                self.params['config']['log'].info(f"[+] {data.get('user_id')} /echo {text}")
            except:
                self.params['config']['log'].warning(f'[!] HTTP post fail')