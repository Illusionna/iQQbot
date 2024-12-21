'''
# System --> Windows & Python3.10.0
# File ----> inherit.py
# Author --> Illusionna
# Create --> 2024/11/28 14:51:30
'''
# -*- Encoding: UTF-8 -*-


import os
import re
from abc import ABCMeta, abstractmethod
from .send import send_message
from .read import read_json, write_json


class Config:
    """普通类：读取 config 配置。"""
    # 是否重载配置。
    reload = False

    @staticmethod
    def load() -> dict:
        """静态函数：加载配置文件。

        Returns:
            dict: 返回配置字典。
        """
        if not os.path.exists(os.path.join(os.getcwd(), 'configs', 'privilege.json')):
            write_json({}, os.path.join(os.getcwd(), 'configs', 'privilege.json'))
        ans = dict()
        ans['init'] = read_json(os.path.join(os.getcwd(), 'configs', 'init.json'))
        ans['privilege'] = read_json(os.path.join(os.getcwd(), 'configs', 'privilege.json'))
        return ans


config = Config.load()


class Run(metaclass=ABCMeta):
    """抽象类：管理功能是否运行，限制派生子类权限。

    Args:
        metaclass (_type_, optional): `"Run"` 由 "`ABCMeta`" 抽象基元类派生。

    .. Contents::
        - `"Run.lock"` 静态变量, 所有派生子类拥有此属性, 用于 `"@Run.authorize()"` 装饰器授权功能开启或禁用。
        - `"Run.run()"` 纯虚函数, 所有派生子类必须重写 `"run(self)"` 以实现具体功能业务。

    .. Usage::
    >>> class Admin_QQ_Bot_Function(Run):
            invoke = '/xxxx'    # 调用方式
            permission = 2      # 二级权限（管理人员及特权者可用）
            # 构造函数无需变动，复制粘贴即可
            def __init__(self, params: dict, *args, **kwargs) -> None:
                super().__init__(*args, **kwargs)
                super().__auto__(self, **locals())
                self.run()
            @Run.authorize()
            def run(self) -> None:
                ... # 具体实现的功能
    """
    lock = False

    @abstractmethod
    def run() -> None:
        """纯虚函数：运行功能。"""
        pass

    @staticmethod
    def authorize() -> 'function':
        """静态函数：授权管理。

        Returns:
            function: 返回闭包函数。
        """
        def decorator(func: 'function') -> 'function':
            def wrapper(self, *args, **kwargs) -> 'function':
                if Config.reload == True:
                    # 重新加载配置文件。
                    global config
                    config = Config.load()
                    Config.reload = False

                level = self.__class__.__dict__.get('permission')
                user_id = self.params['data'].get('user_id')
                invoke = self.__class__.__dict__.get('invoke')
                managers_qq_account_uid = [int(i) for i in config['init']['managers_qq_account_uid']]
                owner_qq_account_uid = int(config['init']['owner_qq_account_uid'])
                privilege = {int(key): value for key, value in config['privilege'].items()}

                # 如果 run(self) 函数上锁了，则停用。
                if self.lock:
                    send_message(f'[!] "{invoke}" 已停用', self.params['config']['socket'], self.params['data'])
                    self.params['config']['log'].warning(f'[!] {user_id} 功能停用 {invoke}')
                    return lambda *args, **kwargs: ...

                # 一级权限，大家都能用。
                if level == 1:
                    return func(self, *args, **kwargs)

                # 二级权限，管理人员及特权者可用。
                elif level == 2:
                    # 如果不是管理人员且不是所有者。注意 and 关键字的短路原理, 管理人员需要写在前面.
                    if (user_id not in managers_qq_account_uid) and (user_id != owner_qq_account_uid):
                        # 如果用户有特权，亦可使用。
                        if (user_id in privilege.keys()) and (invoke in privilege.get(user_id)):
                            return func(self, *args, **kwargs)
                        # 否则指令不可调用。
                        send_message(f'"{invoke}" 指令仅管理人员使用, 可联系 ({owner_qq_account_uid}) 所有者授予特权.', self.params['config']['socket'], self.params['data'])
                        self.params['config']['log'].error(f'[x] {user_id} 普通用户无特权 {invoke}')
                        return lambda *args, **kwargs: ...
                    # 否则是管理人员，指令可调用。
                    return func(self, *args, **kwargs)

                # 三级权限，所有者及特权者可用。
                elif level == 3:
                    # 如果不是所有者。
                    if user_id != owner_qq_account_uid:
                        # 如果是特权者。
                        if (user_id in privilege.keys()) and (invoke in privilege.get(user_id)):
                            return func(self, *args, **kwargs)
                        # 否则指令不可调用。
                        send_message(f'"{invoke}" 指令仅限所有者使用, 可联系 ({owner_qq_account_uid}) 所有者授予特权.', self.params['config']['socket'], self.params['data'])
                        self.params['config']['log'].error(f'[x] {user_id} 普通用户及管理人员无特权 {invoke}')
                        return lambda *args, **kwargs: ...
                    # 否则是所有者，指令可调用。
                    return func(self, *args, **kwargs)

                # 权限不是 1、2、3 个等级，则为异常等级。
                else:
                    self.params['config']['log'].critical(f'[x!] {self.__class__.__name__}.permission 权限异常, 系统自动安排为 3 所有者可用')
                    send_message(f'"{self.__class__.__name__}.permission" 权限异常, 已分配给所有者', self.params['config']['socket'], self.params['data'])
                    if user_id != owner_qq_account_uid:
                        return lambda *args, **kwargs: ...
                    # 所有者可使用异常等级权限的指令。
                    return func(self, *args, **kwargs)

            return wrapper
        return decorator


class Function:
    """普通父类：实现派生子类功能配置的初始化和自动化。
    
    .. Contents::
        - `"Function.__auto__()"` 类函数，用于自动初始化实参。
        - `"Function.add()"` 公有成员函数，用于增加新功能。
        - `"Function.load()"` 公有成员函数，用于加载 QQ 聊天的数据。
        - `"Function.execute()"` 公有成员函数，用于执行一次具体的派生子类功能。
    
    .. Usage::
    >>> class Admin_QQ_Bot_Function(Function):
            invoke = '/yyyy'    # 调用方式
            permission = 1      # 一级权限（大家都可用）
            description = '(づ｡◕‿‿◕｡)づ'    # 功能描述，可写可不写
            # 构造函数无需变动，复制粘贴即可
            def __init__(self, params: dict, *args, **kwargs):
                super().__init__(*args, **kwargs)
                super().__auto__(self, **locals())
                self.run()
            @Run.authorize()
            def run(self) -> None:
                ... # 具体实现的功能
    """

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.invoke = dict()
        self.permission = dict()
        self.description = dict()

    @classmethod
    def __auto__(cls, obj: object, **kwargs) -> None:
        """类函数：用于自动收集派生子类初始化的实参变量。"""
        for key, value in kwargs.items():
            if key not in {'self', 'args', 'kwargs'}:
                setattr(obj, key, value)

    def add(self, cls: object) -> None:
        """公有成员函数：增加新功能。

        Args:
            cls (object): 派生子类。

        .. Usage::
        >>> f = Function()
        >>> f.add(Admin_QQ_Bot_Function)
        """
        # 获取所有派生子类的调用方式。
        invoke: str | None = cls.__dict__.get('invoke')
        if invoke:
            self.invoke[invoke] = cls
        else:
            print(f'\033[31m[x] "{cls.__name__}" 类缺少静态变量 "invoke" 唤起, 须完善该类的代码\033[0m')
            print(f'\033[32m[+] e.g.\t{cls.__name__}.invoke = "/{cls.__name__.lower()}"\033[0m')
            exit(0)

        # 获取所有派生子类的权限等级。
        permission = cls.__dict__.get('permission')
        if permission:
            self.permission[cls.__name__] = permission
        else:
            print(f'\033[31m[x] "{cls.__name__}" 类缺少静态变量 "permission" 权限, 须完善该类的代码\033[0m')
            print(f'\033[32m[+] e.g.\t{cls.__name__}.permission = 1\033[0m')
            exit(0)

        # 获取所有派生子类的简介描述。
        description = cls.__dict__.get('description')
        if description:
            self.description[cls.__name__] = description
        else:
            self.description[cls.__name__] = '开发者很懒 ：）'

    def load(self, params: dict) -> None:
        """公有成员函数：加载 QQ 聊天的数据。

        Args:
            params (dict): HTTP 路由捕获的数据以及配置参数。

        .. Usage::
        >>> f = Function()
        >>> f.add(Admin_QQ_Bot_Function)
        >>> f.load(params)
        """
        self.params = params
        raw_message: str = params['data'].get('raw_message')
        # 如果有消息。
        if raw_message:
            if raw_message[0] == '/':
                raw_message = raw_message.replace('&#91;', '[').replace('&#93;', ']').replace('&amp;', '&').replace('&#44;', ',')
                self.params['data']['raw_message'] = raw_message
                prefix = raw_message.split(' ', 1)[0]
                # 如果用户的消息是在调用指令集，则启用本次功能。
                if prefix in self.invoke.keys():
                    self.prefix = prefix
                    self.lock = False
                else:
                    self.lock = True
            elif raw_message.startswith(f"[CQ:at,qq={config['init']['bot_qq_account_uid']},"):
                send_message(
                    text = f"哈喽，{self.params['data'].get('sender').get('nickname')}，你好呀！(..＞◡＜..)\n\n我叫 {config['init']['bot_name']}，很高兴为你效劳！\n\n你可以使用 /info 指令查看我的介绍。",
                    socket = self.params['config']['socket'],
                    data = self.params['data']
                )
                self.lock = True
            else:
                self.lock = True
        # 否则此处加载的数据无效，给本次功能上锁。
        else:
            self.lock = True

    def execute(self) -> None:
        """公有成员函数：执行一次具体的派生子类功能。

        .. Usage::
        >>> f = Function()
        >>> f.add(Admin_QQ_Bot_Function)
        >>> f.load(params)
        >>> f.execute()
        """
        # 如果功能没上锁，启用状态，则调用指令。
        if not self.lock:
            self.invoke.get(self.prefix)(self.params)


class Help(Function, Run):
    """派生子类：查看帮助。

    Args:
        Function (_type_): 继承 `"Function"` 功能父类。
        Run (_type_): 继承 `"Run"` 抽象父类。

    .. Usage::
    >>> f.add(Help)
    """
    invoke = '/help'    # 使用 /help 唤起。
    permission = 1      # 大家都可用。
    description = '(づ｡◕‿‿◕｡)づ'

    def __init__(self, params: dict, *args, **kwargs) -> None:
        """构造函数：原封不动复制粘贴过来。

        Args:
            params (dict): 默认参数不要动！
        """
        super().__init__(*args, **kwargs)
        super().__auto__(self, **locals())
        self.run()

    @Run.authorize()
    def run(self) -> None:
        """抽象类 `"Run"` 的派生子类 `"Help"` 必须重写 `"run(self)"` 函数具体实现方法。
    
        装饰器 `"@Run.authorize()"` 限制权限。
        """
        data: dict = self.params['data']
        user_id: int = data.get('user_id')
        raw_message: str = data.get('raw_message')

        if raw_message == Help.invoke:
            s = set()

            managers_qq_account_uid = [int(i) for i in config['init']['managers_qq_account_uid']]
            owner_qq_account_uid = int(config['init']['owner_qq_account_uid'])
            privilege = {int(key): value for key, value in config['privilege'].items()}

            invoke: dict = self.params['functions']['invoke']
            permission: dict = self.params['functions']['permission']

            # 普通用户
            if (user_id not in managers_qq_account_uid) and (user_id != owner_qq_account_uid):
                for key, value in invoke.items():
                    if permission[value.__name__] == 1:
                        s.add(('[x' if value.lock else '[+') + f' {key}]')
                if user_id in privilege.keys():
                    for i in privilege[user_id]:
                        s.add(('[x' if invoke[i].lock else '[+') + f' {key}]')
            # 管理人员
            elif user_id in managers_qq_account_uid:
                for key, value in invoke.items():
                    if (permission[value.__name__] == 1) or (permission[value.__name__] == 2):
                        s.add(('[x' if value.lock else '[+') + f' {key}]')
                if user_id in privilege.keys():
                    for i in privilege[user_id]:
                        s.add(('[x' if invoke[i].lock else '[+') + f' {key}]')
            # 所有者
            elif user_id == owner_qq_account_uid:
                for key, value in invoke.items():
                    s.add(('[x' if value.lock else '[+') + f' {key}]')

            docs = ', '.join(s)
            docs = docs + '\n\n+ 表示启用  x 表示停用'

            send_message(docs, self.params['config']['socket'], data)


class Docs(Function, Run):
    """派生子类：查看文档。

    Args:
        Function (_type_): 继承 `"Function"` 功能父类。
        Run (_type_): 继承 `"Run"` 抽象父类。

    .. Usage::
    >>> f.add(Docs)
    """
    invoke = '/docs'    # 使用 /docs 唤起。
    permission = 1      # 大家都可用。
    description = '(づ｡◕‿‿◕｡)づ'

    def __init__(self, params: dict, *args, **kwargs) -> None:
        """构造函数：原封不动复制粘贴过来。

        Args:
            params (dict): 默认参数不要动！
        """
        super().__init__(*args, **kwargs)
        super().__auto__(self, **locals())
        self.run()

    @Run.authorize()
    def run(self) -> None:
        """抽象类 `"Run"` 的派生子类 `"Docs"` 必须重写 `"run(self)"` 函数具体实现方法。
    
        装饰器 `"@Run.authorize()"` 限制权限。
        """
        data: dict = self.params['data']
        user_id: int = data.get('user_id')
        raw_message: str = data.get('raw_message')

        if raw_message == Docs.invoke:
            s = set()

            managers_qq_account_uid = [int(i) for i in config['init']['managers_qq_account_uid']]
            owner_qq_account_uid = int(config['init']['owner_qq_account_uid'])
            privilege = {int(key): value for key, value in config['privilege'].items()}

            invoke: dict = self.params['functions']['invoke']
            permission: dict = self.params['functions']['permission']
            description: dict = self.params['functions']['description']

            # 普通用户
            if (user_id not in managers_qq_account_uid) and (user_id != owner_qq_account_uid):
                for key, value in invoke.items():
                    if permission[value.__name__] == 1:
                        s.add((' [x] 停用 ' if value.lock else ' [+] 启用 ') + key + f'\n\te.g. {description[value.__name__]}')
                if user_id in privilege.keys():
                    for i in privilege[user_id]:
                        s.add((' [x] 停用 ' if invoke[i].lock else ' [+] 启用 ') + i + f'\n\te.g. {description[invoke[i].__name__]}')
            # 管理人员
            elif user_id in managers_qq_account_uid:
                for key, value in invoke.items():
                    if (permission[value.__name__] == 1) or (permission[value.__name__] == 2):
                        s.add((' [x] 停用 ' if value.lock else ' [+] 启用 ') + key + f'\n\te.g. {description[value.__name__]}')
                if user_id in privilege.keys():
                    for i in privilege[user_id]:
                        s.add((' [x] 停用 ' if invoke[i].lock else ' [+] 启用 ') + i + f'\n\te.g. {description[invoke[i].__name__]}')
            # 所有者
            elif user_id == owner_qq_account_uid:
                for key, value in invoke.items():
                    s.add((' [x] 停用 ' if value.lock else ' [+] 启用 ') + key + f'\n\te.g. {description[value.__name__]}')

            docs = '\n'.join(s)

            send_message(docs, self.params['config']['socket'], data)


class Start(Function, Run):
    """派生子类：启用功能。

    Args:
        Function (_type_): 继承 `"Function"` 功能父类。
        Run (_type_): 继承 `"Run"` 抽象父类。

    .. Usage::
    >>> f.add(Start)
    """
    invoke = '/start'   # 唤起方式
    permission = 3      # 仅限所有者可用（不建议授权特权者）
    description = '"/start /x /y" 启用功能'

    def __init__(self, params: dict, *args, **kwargs) -> None:
        """构造函数：原封不动复制粘贴过来。

        Args:
            params (dict): 默认参数不要动！
        """
        super().__init__(*args, **kwargs)
        super().__auto__(self, **locals())
        Start.lock = False      # 该功能类始终保持开启，不可被停用。
        self.run()

    @Run.authorize()
    def run(self) -> None:
        """抽象类 `"Run"` 的派生子类 `"Start"` 必须重写 `"run(self)"` 函数具体实现方法。

        装饰器 `"@Run.authorize()"` 限制权限。
        """
        data: dict = self.params['data']
        raw_message: str = data.get('raw_message')
        text = raw_message.replace(f'{Start.invoke} ', '', 1)

        instructions = set(text.split())
        instructions.discard(Start.invoke)
        instructions.discard(Stop.invoke)
        invoke: dict = self.params['functions']['invoke']
        docs = set()

        if instructions:
            for item in instructions:
                if item in invoke.keys():
                    invoke[item].lock = False
                    docs.add(f' [+] "{item}" 已启用')
                else:
                    docs.add(f' [!] "{item}" 无效指令')
        else:
            docs.add('想启用什么指令呀 ( ´◔︎ ‸◔︎`)')

        send_message('\n'.join(docs), self.params['config']['socket'], data)
        self.params['config']['log'].info(f"[+] {data.get('user_id')} /start {text}")


class Stop(Function, Run):
    """派生子类：停用功能。

    Args:
        Function (_type_): 继承 `"Function"` 功能父类。
        Run (_type_): 继承 `"Run"` 抽象父类。

    .. Usage::
    >>> f.add(Stop)
    """
    invoke = '/stop'    # 唤起方式
    permission = 3      # 仅限所有者可用（不建议授权特权者）
    description = '"/stop /xx /yy" 停用功能'

    def __init__(self, params: dict, *args, **kwargs) -> None:
        """构造函数：原封不动复制粘贴过来。

        Args:
            params (dict): 默认参数不要动！
        """
        super().__init__(*args, **kwargs)
        super().__auto__(self, **locals())
        Stop.lock = False      # 该功能类始终保持开启，不可被自己本身停用。
        self.run()

    @Run.authorize()
    def run(self) -> None:
        """抽象类 `"Run"` 的派生子类 `"Stop"` 必须重写 `"run(self)"` 函数具体实现方法。

        装饰器 `"@Run.authorize()"` 限制权限。
        """
        data: dict = self.params['data']
        raw_message: str = data.get('raw_message')
        text = raw_message.replace(f'{Stop.invoke} ', '', 1)

        instructions = set(text.split())
        instructions.discard(Stop.invoke)
        instructions.discard(Start.invoke)
        invoke: dict = self.params['functions']['invoke']
        docs = set()

        if instructions:
            for item in instructions:
                if item in invoke.keys():
                    invoke[item].lock = True
                    docs.add(f' [-] "{item}" 已停用')
                else:
                    docs.add(f' [!] "{item}" 无效指令')
        else:
            docs.add('你想停用哪些指令 ૮₍ ˃ ⤙ ˂ ₎ა')

        send_message('\n'.join(docs), self.params['config']['socket'], data)
        self.params['config']['log'].info(f"[+] {data.get('user_id')} /stop {text}")


class Power(Function, Run):
    """派生子类：授予特权功能。

    Args:
        Function (_type_): 继承 `"Function"` 功能父类。
        Run (_type_): 继承 `"Run"` 抽象父类。

    .. Usage::
    >>> f.add(Power)
    """
    invoke = '/power'   # 唤起方式
    permission = 3      # 仅限所有者可用（不建议授权特权者）
    description = '/power @小明 /xxx\n\te.g. /power 2141904 /yyy'

    def __init__(self, params: dict, *args, **kwargs) -> None:
        """构造函数：原封不动复制粘贴过来。

        Args:
            params (dict): 默认参数不要动！
        """
        super().__init__(*args, **kwargs)
        super().__auto__(self, **locals())
        self.run()

    @Run.authorize()
    def run(self) -> None:
        """抽象类 `"Run"` 的派生子类 `"Power"` 必须重写 `"run(self)"` 函数具体实现方法。

        装饰器 `"@Run.authorize()"` 限制权限。
        """
        data: dict = self.params['data']
        raw_message: str = data.get('raw_message')
        text = raw_message.replace(f'{Power.invoke} ', '', 1)

        if text != Power.invoke:
            ans = Power.__parse(text)
            if ans:
                if len(ans['who']) != 0:
                    invoke: set = set(self.params['functions']['invoke'].keys())
                    # -------------------------------------------------------
                    # 启用、停用、授权三个功能除了所有者，不建议授予其他用户特权。
                    invoke.discard(Start.invoke)
                    invoke.discard(Stop.invoke)
                    invoke.discard(Power.invoke)
                    # -------------------------------------------------------
                    cmd = ans['cmd']
                    if cmd in invoke:
                        s = set()
                        for i in ans['who']:
                            if i.isdigit():
                                if config['privilege'].get(i):
                                    L: list = config['privilege'].get(i)
                                    L.append(cmd)
                                    config['privilege'][i] = list(set(L))
                                else:
                                    config['privilege'].update({i: [cmd]})
                                s.add(i)
                            else:
                                tmp = i[i.find('qq='):]
                                tmp = tmp[:tmp.find(',')].replace('qq=', '')
                                if tmp == 'all':
                                    pass
                                else:
                                    if config['privilege'].get(tmp):
                                        L: list = config['privilege'].get(tmp)
                                        L.append(cmd)
                                        config['privilege'][tmp] = list(set(L))
                                    else:
                                        config['privilege'].update({tmp: [cmd]})
                                    s.add(tmp)
                        write_json(config['privilege'], os.path.join(os.getcwd(), 'configs', 'privilege.json'))
                        Config.reload = True
                        docs = '\n'.join(s)
                        send_message(f'[+] "{cmd}" 已为以下用户授权\n{docs}', self.params['config']['socket'], data)
                        self.params['config']['log'].info(f"[+] {data.get('user_id')} {text}")
                    else:
                        send_message(f'"{cmd}" 无效 ╭∩╮( ͡⚆ ͜ʖ ͡⚆)╭∩╮', self.params['config']['socket'], data)
                        self.params['config']['log'].warning(f"[+] {data.get('user_id')} {text}")
                else:
                    send_message('格式不对，授权给谁呢 (ﾟω´)', self.params['config']['socket'], data)
                    self.params['config']['log'].warning(f"[+] {data.get('user_id')} {text}")
            else:
                send_message('格式不对哟 ( ×ω× )', self.params['config']['socket'], data)
                self.params['config']['log'].warning(f"[+] {data.get('user_id')} {text}")
        else:
            send_message('想给谁授权什么指令？', self.params['config']['socket'], data)
            self.params['config']['log'].warning(f"[+] {data.get('user_id')} {text}")

    @staticmethod
    def __parse(text: str) -> dict | None:
        """静态私有函数：正则化解析授权指令。

        Args:
            text (str): 文本内容。

        Returns:
            dict | None: 返回字典或者空。
        """
        text = text.strip()
        match = re.match(r'(.*?)\s*\/(\w+)\s*', text)
        if match:
            content_part = match.group(1)
            command = '/' + match.group(2)
            parts = re.findall(r'\d+|(?:\[.*?\])', content_part)
            return {'cmd': command, 'who': parts}
        else:
            return None


class Recall(Function, Run):
    """派生子类：召回特权功能。

    Args:
        Function (_type_): 继承 `"Function"` 功能父类。
        Run (_type_): 继承 `"Run"` 抽象父类。

    .. Usage::
    >>> f.add(Recall)
    """
    invoke = '/recall'  # 唤起方式
    permission = 3      # 仅限所有者可用（不建议授权特权者）
    description = '/recall @小明 /xxx\n\te.g. /recall 2141904 /yyy'

    def __init__(self, params: dict, *args, **kwargs) -> None:
        """构造函数：原封不动复制粘贴过来。

        Args:
            params (dict): 默认参数不要动！
        """
        super().__init__(*args, **kwargs)
        super().__auto__(self, **locals())
        self.run()

    @Run.authorize()
    def run(self) -> None:
        """抽象类 `"Run"` 的派生子类 `"Recall"` 必须重写 `"run(self)"` 函数具体实现方法。

        装饰器 `"@Run.authorize()"` 限制权限。
        """
        data: dict = self.params['data']
        raw_message: str = data.get('raw_message')
        text = raw_message.replace(f'{Recall.invoke} ', '', 1)
        if text != Recall.invoke:
            ans = Recall.__parse(text)
            if ans:
                if len(ans['who']) != 0:
                    invoke: set = set(self.params['functions']['invoke'].keys())
                    # -------------------------------------------------------
                    # 启用、停用、授权三个功能除了所有者，不建议授予其他用户特权。
                    invoke.discard(Start.invoke)
                    invoke.discard(Stop.invoke)
                    invoke.discard(Power.invoke)
                    # -------------------------------------------------------
                    cmd = ans['cmd']
                    if cmd in invoke:
                        s = set()
                        for i in ans['who']:
                            if i.isdigit():
                                if config['privilege'].get(i):
                                    try:
                                        config['privilege'][i].remove(cmd)
                                        s.add(i)
                                    except:
                                        pass
                            else:
                                tmp = i[i.find('qq='):]
                                tmp = tmp[:tmp.find(',')].replace('qq=', '')
                                if tmp == 'all':
                                    pass
                                else:
                                    if config['privilege'].get(tmp):
                                        try:
                                            config['privilege'][tmp].remove(cmd)
                                            s.add(tmp)
                                        except:
                                            pass
                        write_json(config['privilege'], os.path.join(os.getcwd(), 'configs', 'privilege.json'))
                        Config.reload = True
                        docs = '\n'.join(s)
                        send_message(f'[-] 取缔以下用户 "{cmd}" 指令\n{docs}', self.params['config']['socket'], data)
                        self.params['config']['log'].info(f"[+] {data.get('user_id')} {text}")
                    else:
                        send_message(f'"{cmd}" 无效 ╭∩╮( ͡⚆ ͜ʖ ͡⚆)╭∩╮', self.params['config']['socket'], data)
                        self.params['config']['log'].warning(f"[+] {data.get('user_id')} {text}")
                else:
                    send_message('格式不对，取缔谁呢 (ﾟω´)', self.params['config']['socket'], data)
                    self.params['config']['log'].warning(f"[+] {data.get('user_id')} {text}")
            else:
                send_message('格式不对哟 ( ×ω× )', self.params['config']['socket'], data)
                self.params['config']['log'].warning(f"[+] {data.get('user_id')} {text}")
        else:
            send_message('想取消谁的什么指令？', self.params['config']['socket'], data)
            self.params['config']['log'].warning(f"[+] {data.get('user_id')} {text}")

    @staticmethod
    def __parse(text: str) -> dict | None:
        """静态私有函数：正则化解析授权指令。

        Args:
            text (str): 文本内容。

        Returns:
            dict | None: 返回字典或者空。
        """
        text = text.strip()
        match = re.match(r'(.*?)\s*\/(\w+)\s*', text)
        if match:
            content_part = match.group(1)
            command = '/' + match.group(2)
            parts = re.findall(r'\d+|(?:\[.*?\])', content_part)
            return {'cmd': command, 'who': parts}
        else:
            return None