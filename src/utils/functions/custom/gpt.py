import openai
import random
from openai import OpenAI
from ...tools.inherit import Function, Run
from ...tools.send import send_message


class GPT(Function, Run):
    invoke = '/gpt'
    permission = 3

    client = OpenAI(
        # 忘记删除我的密码了，笑死，这里改成你的 openai 账号和密码.
        api_key = 'sk-6kRLYXXXXXXXXXXXXXXXXXXXXXXXXXt8DFZR14eUI',
        base_url = 'https://api.chatanywhere.tech/v1'
    )

    def __init__(self, params: dict, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        super().__auto__(self, **locals())
        self.run()

    @Run.authorize()
    def run(self) -> None:
        data = self.params['data']
        raw_message: str = data.get('raw_message')
        text = raw_message.replace(f'{GPT.invoke} ', '', 1)
        if text != GPT.invoke:
            if text.split():
                rand = random.randint(1, 3)
                try:
                    if rand == 1:
                        ans = GPT.gpt_day_200(text)
                    elif rand == 2:
                        ans = GPT.gpt_count_unknown(text)
                    else:
                        ans = GPT.gpt_hour_60(text)
                except:
                    ans = 'NULL'
                send_message(ans, self.params['config']['socket'], data)
        else:
            send_message(f'格式不正确哦..:)', self.params['config']['socket'], data)

    @staticmethod
    def gpt_day_200(msg: str) -> str:
        response = GPT.client.chat.completions.create(
            model = 'gpt-4o-mini',
            messages = [
                {'role': 'system', 'content': '你是一个群聊机器人'},
                {'role': 'user', 'content': msg}
            ]
        )
        return response.choices[0].message.content

    @staticmethod
    def gpt_count_unknown(msg: str) -> str:
        openai.api_key = 'sk-welLXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXCb8364'
        openai.base_url = 'https://free.v36.cm/v1/'
        openai.default_headers = {'x-foo': 'true'}
        completion = openai.chat.completions.create(
            model = 'gpt-3.5-turbo',
            messages = [
                {
                    'role': 'user',
                    'content': msg,
                },
            ],
        )
        return completion.choices[0].message.content

    @staticmethod
    def gpt_hour_60(msg: str) -> str:
        completion = GPT.client.chat.completions.create(
            model = 'gpt-3.5-turbo',
            messages = [{'role': 'user', 'content': msg}]
        )
        return completion.choices[0].message.content
