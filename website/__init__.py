
from datetime import date, timedelta
from io import BytesIO
import subprocess

from flask import Flask, request, make_response, render_template

import calgen

app = Flask(__name__)

@app.route("/")
def index():
    return render_template('index.html', today=date.today())

@app.route("/chain_calendar.pdf", methods=['GET'])
def get_pdf(extension="pdf"):

    if 'today' in request.args:
        start_date = date.today()
    elif 'tomorrow' in request.args:
        start_date = date.today() + timedelta(days=1)
    else:
        try:
            start_date = date(
                year=int(request.args.get('start_year')),
                month=int(request.args.get('start_month')),
                day=int(request.args.get('start_day')),
            )
        except ValueError as e:
            return '<span style="font-size: 2em; color: red;">Invalid Date</span>'

    pdf_buf = BytesIO()
    calgen.generate_calendar(pdf_buf, start_date)

    if extension == "pdf":
        response = make_response(pdf_buf.getvalue())
        response.headers['Content-Type'] = "application/pdf"
        response.headers['Content-Disposition'] = \
            'inline; filename=calendar.pdf'
        return response

    elif extension == "png":
        proc = subprocess.Popen(
            ["convert", "PDF:-", "-trim", "PNG:-"],
            stdin=subprocess.PIPE, stdout=subprocess.PIPE
        )
        try:
            out, err = proc.communicate(pdf_buf.getvalue(), timeout=2)
        except subprocess.TimeoutExpired:
            proc.kill()
            outs, errs = proc.communicate()

        response = make_response(out)
        response.headers['Content-Type'] = "image/png"
        response.headers['Content-Disposition'] = \
            'inline; filename=calendar.png'
        return response


    else:
        raise ValueError()

@app.route("/chain_calendar.png", methods=['GET'])
def get_png():
    return get_pdf(extension="png")
