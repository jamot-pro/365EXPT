import os, json, time, threading, pty, select, fcntl, termios, struct
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn

app = FastAPI(title="Hermes Agent")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

hermes_fd = None
hermes_pid = None
output_buffer = []
buffer_lock = threading.Lock()

class ChatRequest(BaseModel):
    message: str

def set_winsize(fd, rows, cols):
    try:
        fcntl.ioctl(fd, termios.TIOCSWINSZ, struct.pack('HHHH', rows, cols, 0, 0))
    except:
        pass

def reader_thread():
    global hermes_fd
    while True:
        try:
            r, _, _ = select.select([hermes_fd], [], [], 1.0)
            if r:
                data = os.read(hermes_fd, 65536)
                if not data:
                    break
                with buffer_lock:
                    output_buffer.append(data.decode('utf-8', errors='replace'))
            else:
                with buffer_lock:
                    output_buffer.append("")
        except:
            break

@app.on_event("startup")
async def startup():
    global hermes_fd, hermes_pid
    pid, fd = pty.fork()
    if pid == 0:
        os.environ["TERM"] = "xterm-256color"
        os.execvp("hermes", ["hermes"])
    else:
        hermes_pid = pid
        hermes_fd = fd
        set_winsize(fd, 40, 120)
        fl = fcntl.fcntl(fd, fcntl.F_GETFL)
        fcntl.fcntl(fd, fcntl.F_SETFL, fl | os.O_NONBLOCK)
        t = threading.Thread(target=reader_thread, daemon=True)
        t.start()

@app.get("/health")
async def health():
    alive = True
    try:
        wpid, status = os.waitpid(hermes_pid, os.WNOHANG)
        if wpid == hermes_pid:
            alive = False
    except:
        alive = False
    return {"status": "ok" if alive else "stopped"}

@app.post("/chat")
async def chat(req: ChatRequest):
    if hermes_fd is None:
        raise HTTPException(503, "Hermes not running")
    os.write(hermes_fd, (req.message + "\n").encode())
    time.sleep(1.5)
    lines = []
    with buffer_lock:
        while output_buffer:
            chunk = output_buffer.pop(0)
            if chunk:
                lines.append(chunk)
    return {"response": "".join(lines).strip()}

@app.get("/stream")
async def stream():
    sent = [0]
    async def generate():
        while True:
            new = []
            with buffer_lock:
                count = len(output_buffer)
                if count > sent[0]:
                    new = output_buffer[sent[0]:count]
                    sent[0] = count
            for chunk in new:
                if chunk:
                    yield f"data: {json.dumps({'text': chunk})}\n\n"
                else:
                    yield ": keepalive\n\n"
            import asyncio
            await asyncio.sleep(0.3)
    return StreamingResponse(generate(), media_type="text/event-stream")

HTML_PAGE = """<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Hermes Agent</title>
<style>
*{margin:0;padding:0;box-sizing:border-box}
body{background:#0d0d0d;color:#f0f0f0;font-family:'JetBrains Mono','Fira Code','Courier New',monospace;height:100vh;display:flex;flex-direction:column}
#output{flex:1;overflow-y:auto;padding:16px;white-space:pre-wrap;word-wrap:break-word;font-size:13px;line-height:1.5}
#input-line{display:flex;border-top:1px solid #333;padding:8px 16px;background:#141414}
#prompt{color:#4ade80;margin-right:8px;font-size:13px}
#input{flex:1;background:transparent;border:none;color:#f0f0f0;font-family:inherit;font-size:13px;outline:none}
#input::placeholder{color:#555}
.bar{color:#555;font-size:11px;padding:4px 16px;background:#0a0a0a;border-bottom:1px solid #222;display:flex;justify-content:space-between;user-select:none}
.bar .green{color:#4ade80}
</style>
</head>
<body>
<div class="bar"><span class="green">Hermes Agent v0.19.0</span><span id="conn">connected</span></div>
<div id="output">Starting Hermes...</div>
<div id="input-line"><span id="prompt">&gt;</span><input id="input" type="text" placeholder="Type a message..." autofocus/></div>
<script>
const out=document.getElementById('output'), inp=document.getElementById('input');
let buf='';
const es=new EventSource('/stream');
es.onmessage=e=>{if(e.data&&e.data!=''){const m=JSON.parse(e.data);if(m.text){buf+=m.text;out.textContent=buf;out.scrollTop=out.scrollHeight}}};
inp.addEventListener('keydown',async e=>{if(e.key==='Enter'&&inp.value.trim()){const m=inp.value;buf+='\\n> '+m+'\\n';out.textContent=buf;const v=inp.value;inp.value='';try{const r=await fetch('/chat',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({message:m})});const d=await r.json();buf+=d.response+'\\n';out.textContent=buf;out.scrollTop=out.scrollHeight}catch(e){buf+='\\n[Error]\\n';out.textContent=buf}}});
</script>
</body>
</html>"""

@app.get("/", response_class=HTMLResponse)
async def index():
    return HTML_PAGE

if __name__ == "__main__":
    port = int(os.getenv("PORT", 10000))
    uvicorn.run("hermes_wrapper:app", host="0.0.0.0", port=port, log_level="info", reload=False)
