import os, json, time, threading, urllib.request
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

TOKEN = os.environ["BOT_TOKEN"]
API = "https://botapi.rubika.ir/v3/" + TOKEN + "/"
PAGES = ["📄 صفحه ۱", "📄 صفحه ۲", "📄 صفحه ۳", "📄 صفحه ۴", "📄 صفحه ۵"]

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
def keypad(i):
    b = []
    if i > 0:
        b.append({"id": "p_%d" % (i - 1), "type": "Simple", "button_text": "◀️ قبلی"})
    if i < len(PAGES) - 1:
        b.append({"id": "p_%d" % (i + 1), "type": "Simple", "button_text": "بعدی ▶️"})
    return {"rows": [{"buttons": b}]}

def handle(body):
    try:
        print("IN", str(body)[:200])
        if "inline_message" in body:
            m = body["inline_message"]
            bid = m.get("button_id") or (m.get("aux_data") or {}).get("button_id")
            i = int(bid.split("_")[1])
            call("editMessageText", {"chat_id": m["chat_id"],
                 "message_id": m["message_id"], "text": PAGES[i]})
            call("editMessageKeypad", {"chat_id": m["chat_id"],
                 "message_id": m["message_id"], "inline_keypad": keypad(i)})
        elif "update" in body:
            u = body["update"]
            if u.get("type") == "NewMessage":
                call("sendMessage", {"chat_id": u["chat_id"],
                     "text": PAGES[0], "inline_keypad": keypad(0)})
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
