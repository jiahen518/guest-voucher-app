import os, json, csv, io
from datetime import datetime, timedelta
from flask import Flask, request, render_template, send_file

app = Flask(__name__)

VOUCHER_FILE = "vouchers.json"
CLAIM_LOG = "claims.csv"

def init_vouchers():
    if not os.path.exists(VOUCHER_FILE):
        vouchers = [{"code": f"GUEST{str(i).zfill(3)}", "used": False} for i in range(1, 101)]
        with open(VOUCHER_FILE, "w") as f:
            json.dump(vouchers, f, indent=2)

def load_vouchers():
    with open(VOUCHER_FILE) as f:
        return json.load(f)

def save_vouchers(vouchers):
    with open(VOUCHER_FILE, "w") as f:
        json.dump(vouchers, f, indent=2)

def log_claim(name, company, ip, code):
    file_exists = os.path.isfile(CLAIM_LOG)
    write_header = not file_exists or os.stat(CLAIM_LOG).st_size == 0

    with open(CLAIM_LOG, "a", newline="") as f:
        writer = csv.writer(f)
        if write_header:
            writer.writerow(["Timestamp", "Name", "Company", "IP", "VoucherCode"])

        timestamp = (datetime.utcnow() + timedelta(hours=8)).strftime("%Y-%m-%d %H:%M:%S")
        writer.writerow([timestamp, name, company, ip, code])


init_vouchers()

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "GET":
        return render_template("index.html")

    name = request.form.get("name")
    company = request.form.get("company")
    ip = request.remote_addr

    vouchers = load_vouchers()
    unused = next((v for v in vouchers if not v["used"]), None)
    
    if not unused:
        return render_template("voucher.html", code=None)
    
    unused["used"] = True
    save_vouchers(vouchers)
    log_claim(name, company, ip, unused["code"])
    
    return render_template("voucher.html", code=unused["code"])

@app.route("/qr")
def qr():
    import qrcode
    img = qrcode.make(request.host_url)
    buf = io.BytesIO()
    img.save(buf, format='PNG')
    buf.seek(0)
    return send_file(buf, mimetype='image/png')


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
