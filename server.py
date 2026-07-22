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

import websockets

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


def check_auth(headers, message=None):
    auth = ''
    if headers and 'authorization' in headers:
        auth = headers['authorization']
    elif message and isinstance(message, str) and message.startswith('{'):
        try:
            cmd = json.loads(message)
            return cmd.get('user') == HERMES_USER and cmd.get('pass') == HERMES_PASS
        except json.JSONDecodeError:
            pass

    if not auth.startswith('Basic '):
        return False
    try:
        decoded = base64.b64decode(auth[6:]).decode('utf-8')
        user, _, password = decoded.partition(':')
        return user == HERMES_USER and password == HERMES_PASS
    except Exception:
        return False


async def handler(websocket, path=None):
    if path == '/ws':
        first_msg = await asyncio.wait_for(websocket.recv(), timeout=5)
        if not check_auth({}, message=first_msg):
            await websocket.close(4001, 'Unauthorized')
            return

        session = TerminalSession()
        session.spawn()

        async def reader():
            try:
                while True:
                    data = session.read()
                    if data is None:
                        break
                    if data:
                        await websocket.send(data)
                    await asyncio.sleep(0.01)
            except websockets.exceptions.ConnectionClosed:
                pass
            finally:
                session.close()

        async def writer():
            try:
                async for message in websocket:
                    if isinstance(message, str) and message.startswith('{'):
                        try:
                            cmd = json.loads(message)
                            if cmd.get('type') == 'resize':
                                session.set_winsize(cmd.get('cols', 80), cmd.get('rows', 24))
                                continue
                        except json.JSONDecodeError:
                            pass
                    if isinstance(message, str):
                        session.write(message)
            except websockets.exceptions.ConnectionClosed:
                pass
            finally:
                session.close()

        await asyncio.gather(reader(), writer())
    else:
        await websocket.close(1000, 'OK')


async def process_request(path, request_headers):
    if path == '/health':
        headers = [('Content-Type', 'text/plain'), ('Server', 'HermesWeb/1.0')]
        return (200, headers, b'OK')

    if path in ('/', ''):
        if not check_auth(request_headers):
            headers = [('WWW-Authenticate', 'Basic realm="Hermes Agent"'), ('Content-Type', 'text/plain'), ('Server', 'HermesWeb/1.0')]
            return (401, headers, b'Unauthorized')
        headers = [('Content-Type', 'text/html; charset=utf-8'), ('Server', 'HermesWeb/1.0')]
        return (200, headers, INDEX_HTML.encode())

    return None


async def main():
    async with websockets.serve(
        handler,
        host='0.0.0.0',
        port=PORT,
        process_request=process_request,
    ):
        print(f'Serving on port {PORT}', flush=True)
        await asyncio.Future()


if __name__ == '__main__':
    asyncio.run(main())
