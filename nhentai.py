from flask import Flask, render_template, request, redirect, url_for, flash, make_response
import subprocess
import os

latest_log_output = ""

app = Flask(__name__, template_folder='./html')
app.secret_key = os.urandom(24)

# 密碼從環境變數讀取，若沒設定則預設為 "admin"
PASSWORD = os.getenv("NHENTAI_PASSWORD", "admin")

# 下載相關設定
DOWNLOAD_PATH = "/nhentai"
DEFAULT_FORMAT = "%a%t"

def run_nhentai_command(args):
    global latest_log_output
    try:
        result = subprocess.run(args, capture_output=True, text=True)
        output = result.stdout + result.stderr
        latest_log_output = output  # ⬅️ 儲存最近 log

        if "main: 🍻 All done." in output:
            flash("✅ Dowload success", "success")
        elif "cmd_parser: User-Agent saved" in output:
            flash("✅ User-Agent saved", "success")
        elif "cmd_parser: Cookie saved" in output:
            flash("✅ Cookie saved", "success")
        elif result.returncode == 0:
            flash("⚠️ Error, completed without success", "error")
        else:
            flash("❌ Fail", "error")

    except Exception as e:
        latest_log_output = str(e)
        flash(f"❌ Unexpected error：{e}", "error")


@app.route('/')
def index():
    password_cookie = request.cookies.get("nhentai_auth")
    is_verified = password_cookie == "ok"
    return render_template("index.html", password=PASSWORD, verified=is_verified)

@app.route('/debug-log')
def debug_log():
    return latest_log_output, 200, {"Content-Type": "text/plain; charset=utf-8"}


@app.route('/verify-password', methods=['POST'])
def verify_password():
    password = request.form.get("password", "")
    if password == PASSWORD:
        resp = make_response(redirect(url_for("index")))
        resp.set_cookie("nhentai_auth", "ok", max_age=60*60*24*30)  # 有效期30天
        return resp
    else:
        flash("Wrong password", "error")
        return redirect(url_for("index"))

@app.route('/ua', methods=['POST'])
def ua():
    ua = request.form.get('ua', '').strip()
    if not ua or len(ua) > 200:
        flash("User-Agent error ❌", "error")
        return redirect(url_for('index'))
    run_nhentai_command(["nhentai", "--useragent", ua])
    return redirect(url_for('index'))

@app.route('/cookies', methods=['POST'])
def cookies():
    ck = request.form.get('ck', '').strip()
    if not ck or len(ck) > 1000:
        flash("Cookie error ❌", "error")
        return redirect(url_for('index'))
    run_nhentai_command(["nhentai", "--cookie", ck])
    return redirect(url_for('index'))

@app.route('/download', methods=['POST'])
def download():
    gallery_id = request.form.get('id', '').strip()
    if not gallery_id.isdigit():
        flash("ID Must be 6 digit ❌", "error")
        return redirect(url_for('index'))

    command = [
        "nhentai", "--id", gallery_id,
        "--page-all", "--download", "--delay", "1",
        "--cbz", "--format", DEFAULT_FORMAT,
        "--rm-origin-dir", "--output", DOWNLOAD_PATH
    ]
    run_nhentai_command(command)
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=61234)
