from flask import Flask, request
import json

app = Flask(__name__)

@app.post("/webhook")
def webhook():
    print("=== ALERT RECEIVED ===")
    print("Headers:", dict(request.headers))
    print("Raw body:", request.data.decode("utf-8", errors="ignore"))

    payload = request.get_json(silent=True)
    if payload is not None:
        print("JSON:", json.dumps(payload, ensure_ascii=False, indent=2))

    return {"status": "ok"}

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8081)
