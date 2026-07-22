import subprocess, json, os, signal, select, fcntl, sys, time
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn

app = FastAPI(title="Hermes Agent HTTP Wrapper")

@app.get("/")
async def root():
    return {
        "service": "Hermes Agent HTTP Wrapper",
        "status": "running" if hermes_proc and hermes_proc.poll() is None else "stopped",
        "endpoints": {
            "GET /health": "health check",
            "POST /chat": "send a message to Hermes"
        }
    }

class ChatRequest(BaseModel):
    message: str

hermes_proc = None

@app.on_event("startup")
async def startup():
    global hermes_proc
    env = os.environ.copy()
    env["TERM"] = "xterm-256color"
    env["NON_INTERACTIVE"] = "1"
    hermes_proc = subprocess.Popen(
        ["hermes"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        env=env, text=True, bufsize=1
    )

@app.get("/health")
async def health():
    if hermes_proc and hermes_proc.poll() is None:
        return {"status": "ok"}
    return {"status": "stopped"}

@app.post("/chat")
async def chat(req: ChatRequest):
    if not hermes_proc or hermes_proc.poll() is not None:
        raise HTTPException(503, "Hermes not running")
    hermes_proc.stdin.write(req.message + "\n")
    hermes_proc.stdin.flush()
    time.sleep(1)
    out = ""
    while True:
        try:
            line = hermes_proc.stdout.readline()
            if not line:
                break
            out += line
        except:
            break
    return {"response": out.strip()}

if __name__ == "__main__":
    port = int(os.getenv("PORT", 10000))
    uvicorn.run("hermes_wrapper:app", host="0.0.0.0", port=port, log_level="info", reload=False)
