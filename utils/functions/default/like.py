import requests
from ...tools.inherit import Function, Run
from ...tools.send import send_message


class SendLike(Function, Run):
    invoke = '/点赞'
    permission = 1

    def __init__(self, params: dict, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        super().__auto__(self, **locals())
        self.run()

    @Run.authorize()
    def run(self) -> None:
        data = self.params['data']
        raw_message: str = data.get('raw_message')
        url = f"http://{self.params['config']['socket']}/send_like"
        user_id = data.get('user_id')
        json = {'user_id': user_id, 'times': 10}

        if raw_message == SendLike.invoke:
            requests.post(url, json=json, timeout=5)
            send_message('已赞, 每日上限 10 次 O(∩_∩)O', self.params['config']['socket'], data)