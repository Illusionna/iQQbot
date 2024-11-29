'''
# System --> Windows & Python3.10.0
# File ----> send.py
# Author --> Illusionna
# Create --> 2024/11/28 14:59:31
'''
# -*- Encoding: UTF-8 -*-


import requests


def send_message(text: str, socket: str, data: dict, timeout: int = 5) -> None:
    """普通函数：机器人给调用者发送消息。

    Args:
        text (str): 发送的文本。
        socket (str): QQ 机器人 HTTP 服务监听套接字。
        data (dict): 默认数据包，不可变动！
        timeout (int, optional): 超时处理，默认 5 秒。
    """
    user_id: int = data.get('user_id')
    group_id: int | None = data.get('group_id')
    message_id: int = data.get('message_id')
    url = f'http://{socket}'
    msg = {'message': f'[CQ:reply,id={message_id}]{text}'}
    if group_id is not None:
        url = url + '/send_group_msg'
        msg.update({'group_id': group_id})
    else:
        url = url + '/send_private_msg'
        msg.update({'user_id': user_id})
    requests.post(url, json=msg, timeout=timeout)