import psutil
import platform
from ...tools.inherit import Function, Run
from ...tools.send import send_message


class System(Function, Run):
    invoke = '/system'
    permission = 3
    description = '查看系统设备'

    def __init__(self, params: dict, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        super().__auto__(self, **locals())
        self.run()

    @Run.authorize()
    def run(self) -> None:
        data = self.params['data']
        raw_message: str = data.get('raw_message')
        if raw_message == System.invoke:
            docs = ''

            docs = docs + '- OS\n' + f'\t{platform.uname().system}\n\t{platform.uname().machine}\n\t{platform.uname().version}\n'

            docs = docs + '- CPU\n' + f'\t{platform.processor()}\n\t{platform.architecture()}\n\t负载率：{psutil.cpu_percent(interval=0.5)}%\n\t线程逻辑数：{psutil.cpu_count(logical=True)}\n\t核心物理数：{psutil.cpu_count(logical=False)}\n\t频率：当前 {psutil.cpu_freq().current:.1f} Mhz 最小 {psutil.cpu_freq().min} Mhz 最大 {psutil.cpu_freq().max} Mhz\n'

            docs = docs + '- RAM\n' + f'\t负载率：{psutil.virtual_memory().percent}%\n\t总计：{psutil.virtual_memory().total / (1 << 30):.3f} GB\n\t可用：{psutil.virtual_memory().available / (1 << 30):.3f} GB\n\t自由：{psutil.virtual_memory().free / (1 << 30):.3f} GB\n\t已用：{psutil.virtual_memory().used / (1 << 30):.3f} GB\n'

            docs = docs + '- SWAP\n' + f'\t负载率：{psutil.swap_memory().percent}%\n\t总计：{psutil.swap_memory().total / (1 << 30):.3f} GB\n\t已用：{psutil.swap_memory().used / (1 << 30):.3f} GB\n\t自由：{psutil.swap_memory().free / (1 << 30):.3f} GB\n\t从磁盘累计换入：{psutil.swap_memory().sin / (1 << 30):.3f} GB\n\t从磁盘累计换出：{psutil.swap_memory().sout / (1 << 30):.3f} GB'

            send_message(docs, self.params['config']['socket'], data)