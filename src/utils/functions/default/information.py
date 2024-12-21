import os
import requests
from ...tools.inherit import Function, Run
from ...tools.send import send_message
from ...tools.read import read_json


class Info(Function, Run):
    invoke = '/info'
    permission = 1
    description = '机器人相关信息'

    def __init__(self, params: dict, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        super().__auto__(self, **locals())
        self.run()

    @Run.authorize()
    def run(self) -> None:
        data: dict = self.params['data']
        raw_message: str = data.get('raw_message')
        if raw_message == Info.invoke:
            json = read_json(os.path.join('configs', 'init.json'))
            url = f"http://{self.params['config']['socket']}/get_stranger_info"
            bot_name = json['bot_name']
            bot_qq_account_uid = int(json['bot_qq_account_uid'])
            owner_qq_account_uid = int(json['owner_qq_account_uid'])
            managers_qq_account_uid = list(str(i) for i in iter(json['managers_qq_account_uid']))
            
            try:
                bot_nickname = requests.post(url, {'user_id': bot_qq_account_uid}, timeout=5).json().get('data').get('nickname')
            except:
                bot_nickname = None
            try:
                owner_nickname = requests.post(url, {'user_id': owner_qq_account_uid}, timeout=5).json().get('data').get('nickname')
            except:
                owner_nickname = None

            docs = f"嗨，{data.get('sender').get('nickname')}，你好！ ξ( ✿＞◡❛)\n\n"
            
            if bot_nickname:
                docs = docs + f'我叫 "{bot_name}"，你也可以艾特 "@{bot_nickname}" 我。\n\n'
            else:
                docs = docs + f'我叫 "{bot_name}"。\n\n'
            if owner_nickname:
                docs = docs + f'我是由 "@{owner_nickname}" ({owner_qq_account_uid}) 开发的架构。'
            else:
                docs = docs + f'我是由 {owner_qq_account_uid} 开发的架构。'
            if managers_qq_account_uid:
                docs = docs + f"此外，我的管理人员 {', '.join(managers_qq_account_uid)} 是我最好的朋友。ta 们为我赋予机器人的功能。"
            else:
                docs = docs + 'ta 为我赋予机器人的功能。'
            docs = docs + '\n\n你可使用 /help 和 /docs 指令查看帮助文档，如果你在使用中遇到问题，欢迎咨询开发者。\n\n祝您生活愉快！ ლ(╹◡╹ლ)'

            send_message(docs, self.params['config']['socket'], data)
