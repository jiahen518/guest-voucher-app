import os, json
from flask import Flask, render_template, render_template_string

import io, qrcode
from flask import send_file, request


BASE_DIR      = (__file__)
TEMPLATES_DIR = "templates"
VOUCHER_FILE  = "vouchers.json"

app = Flask(__name__, template_folder=TEMPLATES_DIR)
app.debug = True

def load_vouchers():
    with open(VOUCHER_FILE) as f:
        return json.load(f)

def save_vouchers(vs):
    with open(VOUCHER_FILE, "w") as f:
        json.dump(vs, f, indent=2)

def init_vouchers():
    if not os.path.exists(VOUCHER_FILE):
        vs = [{"code": f"GUEST{str(i).zfill(3)}", "used": False} for i in range(1,101)]
        save_vouchers(vs)

init_vouchers()

@app.route("/__health")
def health():
    return "OK"

@app.route("/__list_templates__")
def list_templates():
    exists = os.path.isdir(TEMPLATES_DIR)
    files = os.listdir(TEMPLATES_DIR) if exists else []
    return {"templates_dir": TEMPLATES_DIR, "exists": exists, "files": files}

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/get-voucher")
def get_voucher():
    vs = load_vouchers()
    u = next((v for v in vs if not v["used"]), None)
    if not u:
        return render_template("voucher.html", code=None)
    u["used"] = True
    save_vouchers(vs)
    return render_template("voucher.html", code=u["code"])

@app.route("/qr.png")
def portal_qr():
    target = request.host_url           
    img = qrcode.make(target)             
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)
    return send_file(buf, mimetype="image/png")

if __name__ == "__main__":
    print("BASE_DIR:", BASE_DIR)
    print("TEMPLATES_DIR:", TEMPLATES_DIR, "| exists:", os.path.isdir(TEMPLATES_DIR))
    if os.path.isdir(TEMPLATES_DIR):
        print("Templates:", os.listdir(TEMPLATES_DIR))
    app.run(host="0.0.0.0", port=5000)
