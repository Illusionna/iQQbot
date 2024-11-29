'''
# System --> Windows & Python3.10.0
# File ----> main.py
# Author --> Illusionna
# Create --> 2024/11/29 00:37:59
'''
# -*- Encoding: UTF-8 -*-


import os
import uvicorn
from fastapi import FastAPI, Request
from utils.tools.read import read_json
from utils.tools.log_colour import create_logging
from utils.tools.inherit import Function, Help, Docs, Power, Recall, Start, Stop

from utils.functions.default.echo import Echo
from utils.functions.default.device import System
from utils.functions.default.privilege import Privilege
from utils.functions.default.information import Info
from utils.functions.default.like import SendLike
from utils.functions.custom.stochastic.stochastic import GenerateFloatNumber, Sample


f = Function()
app = FastAPI()
log = create_logging(log_path='日志.log')
service = read_json(os.path.join('configs', 'init.json'))
# -------------------------------------------------------------------------------------
f.add(Help); f.add(Docs); f.add(Power); f.add(Recall); f.add(Start); f.add(Stop)
# -------------------------------------------------------------------------------------
f.add(Echo)
f.add(System)
f.add(Privilege)
f.add(Info)
f.add(SendLike)
f.add(Sample)
f.add(GenerateFloatNumber)


@app.post('/')
async def Main(request: Request) -> str:
    params = {
        'data': await request.json(),
        'config': {
            'log': log,
            'socket': service['http_service_listening_socke']
        },
        'functions': {
            'invoke': f.invoke,
            'permission': f.permission,
            'description': f.description
        }
    }
    f.load(params)
    f.execute()
    return 'OK'



if __name__ == '__main__':
    print('\n从 QQ 艾特你的机器人开启之旅！\n')
    uvicorn.run(
        app = f"{os.path.basename(__file__).split('.')[0]}:app",
        host = service['http_app_host'],
        port = service['http_app_port'],
        reload = False
    )