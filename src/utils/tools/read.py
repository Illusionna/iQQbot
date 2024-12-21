'''
# System --> Windows & Python3.10.0
# File ----> read.py
# Author --> Illusionna
# Create --> 2024/11/28 14:59:39
'''
# -*- Encoding: UTF-8 -*-


import json


def read_json(path: str) -> dict:
    """普通函数：读取 json 文件。

    Args:
        path (str): 文件路径。

    Returns:
        dict: 返回字典。
    """
    with open(path, mode='r', encoding='utf-8') as f:
        ans: dict = json.load(f)
    return ans


def write_json(data: dict, path: str) -> None:
    """普通函数：保存 json 文件。

    Args:
        data (dict): 数据字典。
        path (str): 保存路径。
    """
    with open(path, mode='w', encoding='utf-8') as f:
        json.dump(obj = data, fp = f, ensure_ascii = False, indent = 4)