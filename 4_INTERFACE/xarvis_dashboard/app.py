from flask import Flask, render_template
import os

app = Flask(__name__)

@app.route("/")
def dashboard():
    sekhmet_output = os.popen("python3 sekhmet_engine.py").read()
    mamba_output = os.popen("bash mamba_watchdog.sh").read()
    return render_template("dashboard.html", sekhmet=sekhmet_output, mamba=mamba_output)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
