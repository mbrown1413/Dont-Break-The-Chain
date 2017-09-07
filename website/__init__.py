
from datetime import date
from io import BytesIO

from flask import Flask, request, make_response, render_template

import calgen

app = Flask(__name__)

@app.route("/")
def index():
    return render_template('index.html', today=date.today())

@app.route("/calendar.pdf", methods=['GET'])
def get_pdf():

    #TODO: Validate this data
    start_date = date(
        year=int(request.args.get('start_year')),
        month=int(request.args.get('start_month')),
        day=int(request.args.get('start_day')),
    )

    buf = BytesIO()
    calgen.generate_calendar(buf, start_date)

    response = make_response(buf.getvalue())
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = \
        'inline; filename=calendar.pdf'
    return response
