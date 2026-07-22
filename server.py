import asyncio
import base64
import html
import json
import os
import pty
import signal
import struct
import termios
import fcntl

import aiohttp
from aiohttp import web

PORT = int(os.environ.get('PORT', 10000))
HERMES_CMD = os.environ.get('HERMES_CMD', 'hermes')
HERMES_USER = os.environ.get('HERMES_USER', 'hermes')
HERMES_PASS = os.environ.get('HERMES_PASS', 'hermes123')

_u = html.escape(HERMES_USER)
_p = html.escape(HERMES_PASS)
INDEX_HTML = """<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width,initial-scale=1"/>
<title>Hermes Agent</title>
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/xterm/css/xterm.css"/>
<style>*{margin:0;padding:0;box-sizing:border-box}html,body,#terminal{width:100%;height:100%;background:#000}</style>
</head>
<body><div id="terminal"></div>
<script src="https://cdn.jsdelivr.net/npm/xterm/lib/xterm.js"></script>
<script src="https://cdn.jsdelivr.net/npm/xterm-addon-fit/lib/xterm-addon-fit.js"></script>
<script>
var term=new Terminal({cursorBlink:true,fontSize:14,theme:{background:'#000',foreground:'#fff'}});
var fitAddon=new FitAddon.FitAddon();
term.loadAddon(fitAddon);
term.open(document.getElementById('terminal'));
fitAddon.fit();
var ws=new WebSocket((location.protocol==='https:'?'wss:':'ws:')+'//'+location.host+'/ws');
ws.onopen=function(){ws.send(JSON.stringify({type:'auth',user:'_UU_',pass:'_PP_'}));term.focus()};
ws.onmessage=function(e){term.write(e.data)};
ws.onclose=function(){term.write('\\r\\nConnection closed\\r\\n')};
term.onData(function(d){ws.send(d)});
term.onResize(function(e){ws.send(JSON.stringify({type:'resize',cols:e.cols,rows:e.rows}))});
window.addEventListener('resize',function(){fitAddon.fit();var d=term;ws.send(JSON.stringify({type:'resize',cols:d.cols,rows:d.rows}))});
</script></body></html>""".replace('_UU_', _u).replace('_PP_', _p)


def check_auth(headers):
    auth = headers.get('Authorization', '')
    if not auth.startswith('Basic '):
        return False
    try:
        decoded = base64.b64decode(auth[6:]).decode('utf-8')
        user, _, password = decoded.partition(':')
        return user == HERMES_USER and password == HERMES_PASS
    except Exception:
        return False


class TerminalSession:
    def __init__(self):
        self.child_fd = None
        self.pid = None

    def spawn(self):
        self.pid, self.child_fd = pty.fork()
        if self.pid == 0:
            signal.signal(signal.SIGCHLD, signal.SIG_DFL)
            os.execvp('sh', ['sh', '-c', HERMES_CMD])
        else:
            self.set_winsize(80, 24)

    def set_winsize(self, cols, rows):
        if self.child_fd:
            size = struct.pack("HHHH", rows, cols, 0, 0)
            fcntl.ioctl(self.child_fd, termios.TIOCSWINSZ, size)

    def read(self):
        try:
            data = os.read(self.child_fd, 65536)
            return data.decode('utf-8', errors='replace')
        except OSError:
            return None

    def write(self, data):
        try:
            os.write(self.child_fd, data.encode('utf-8'))
        except OSError:
            pass

    def close(self):
        if self.child_fd:
            try:
                os.close(self.child_fd)
            except OSError:
                pass
            self.child_fd = None
        if self.pid and self.pid > 0:
            try:
                os.kill(self.pid, signal.SIGHUP)
                os.waitpid(self.pid, 0)
            except OSError:
                pass


async def handle_health(request):
    return web.Response(text='OK')

async def handle_index(request):
    if not check_auth(request.headers):
        raise web.HTTPUnauthorized(headers={'WWW-Authenticate': 'Basic realm="Hermes Agent"'})
    return web.Response(text=INDEX_HTML, content_type='text/html')

async def handle_ws(request):
    first_msg = None
    async def check_auth_ws():
        nonlocal first_msg
        msg = await ws.receive()
        if msg.type == aiohttp.WSMsgType.TEXT:
            first_msg = msg.data
            try:
                cmd = json.loads(msg.data)
                if cmd.get('type') == 'auth':
                    if cmd.get('user') == HERMES_USER and cmd.get('pass') == HERMES_PASS:
                        return True
                    else:
                        await ws.close(code=4001, message=b'Unauthorized')
                        return False
            except json.JSONDecodeError:
                pass
            if not check_auth(request.headers):
                await ws.close(code=4001, message=b'Unauthorized')
                return False
            return True
        else:
            await ws.close(code=4001, message=b'Unauthorized')
            return False

    ws = web.WebSocketResponse(max_msg_size=0)
    await ws.prepare(request)

    if not check_auth(request.headers):
        timed_out = False
        try:
            msg = await asyncio.wait_for(ws.receive(), timeout=5)
            if msg.type == aiohttp.WSMsgType.TEXT:
                try:
                    cmd = json.loads(msg.data)
                    if cmd.get('type') == 'auth':
                        if not (cmd.get('user') == HERMES_USER and cmd.get('pass') == HERMES_PASS):
                            return ws
                    else:
                        return ws
                except json.JSONDecodeError:
                    return ws
            else:
                return ws
        except asyncio.TimeoutError:
            return ws

    session = TerminalSession()
    session.spawn()

    async def reader():
        try:
            while True:
                data = session.read()
                if data is None:
                    break
                if data:
                    await ws.send_str(data)
                await asyncio.sleep(0.01)
        except Exception:
            pass
        finally:
            session.close()

    async def writer():
        try:
            async for msg in ws:
                if msg.type == aiohttp.WSMsgType.TEXT:
                    text = msg.data
                    if text.startswith('{'):
                        try:
                            cmd = json.loads(text)
                            if cmd.get('type') == 'resize':
                                session.set_winsize(cmd.get('cols', 80), cmd.get('rows', 24))
                                continue
                        except json.JSONDecodeError:
                            pass
                    session.write(text)
                elif msg.type == aiohttp.WSMsgType.ERROR:
                    break
        except Exception:
            pass
        finally:
            session.close()

    await asyncio.gather(reader(), writer())
    return ws


async def main():
    app = web.Application()
    app.router.add_get('/health', handle_health)
    app.router.add_head('/health', handle_health)
    app.router.add_get('/', handle_index)
    app.router.add_head('/', handle_index)
    app.router.add_get('/ws', handle_ws)

    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', PORT)
    await site.start()
    print(f'Serving on port {PORT}', flush=True)
    await asyncio.Future()


if __name__ == '__main__':
    asyncio.run(main())
