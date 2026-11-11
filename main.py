import os, json, time, threading, urllib.request
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

TOKEN = os.environ["BOT_TOKEN"]
API = "https://botapi.rubika.ir/v3/" + TOKEN + "/"
HELLO = "سلام 👋\nمن یارگپ هستم.\nاین یک پیام تست است."

def call(method, data):
    t = time.time()
    req = urllib.request.Request(API + method, json.dumps(data).encode(),
                                 {"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=15) as r:
            res = json.loads(r.read())
        print("T", method, round(time.time() - t, 2))
        return res
    except Exception as e:
        print("ERR", method, e)

def handle(body):
    try:
        u = body.get("update")
        if u and u.get("type") == "NewMessage":
            print("GOT", u["chat_id"])
            call("sendMessage", {"chat_id": u["chat_id"], "text": HELLO})
    except Exception as e:
        print("ERR handle", e)

class H(BaseHTTPRequestHandler):
    def _ok(self):
        self.send_response(200)
        self.send_header("Content-Length", "2")
        self.end_headers()
        self.wfile.write(b"ok")
    def do_GET(self):
        self._ok()
    def do_POST(self):
        n = int(self.headers.get("Content-Length", 0))
        try:
            body = json.loads(self.rfile.read(n) or b"{}")
        except Exception:
            body = {}
        self._ok()
        threading.Thread(target=handle, args=(body,), daemon=True).start()
    def log_message(self, *a):
        pass

def register():
    d = os.environ.get("RAILWAY_PUBLIC_DOMAIN")
    if not d:
        print("no domain yet")
        return
    for t in ("ReceiveUpdate", "ReceiveInlineMessage"):
        print(t, call("updateBotEndpoints", {"url": "https://" + d + "/" + t, "type": t}))

if __name__ == "__main__":
    threading.Timer(3, register).start()
    ThreadingHTTPServer(("0.0.0.0", int(os.environ.get("PORT", 8080))), H).serve_forever()
