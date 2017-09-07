# Don't Break the Chain calendar
#
# Design based on:
# http://karenkavett.com/blog/3555/dont-break-the-chain-calendar-2017-free-motivational-tool-printable.php

from datetime import date, timedelta
from copy import copy

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter, A4


COLOR_BLACK = "#000000"
COLOR_GRAY = "#555555"
def get_month_color(d):
    if (d.year + d.month) % 2 == 0:
        return COLOR_BLACK
    else:
        return COLOR_GRAY

def add_one_year(d):
    """Calculates the number of days until the same date next year."""
    same_day_next_year = d + timedelta(days=365)

    # Starting on the leap day?
    if (d.month, d.day) == (2, 29):
        return same_day_next_year

    # Does the time period include a leap year?
    if same_day_next_year.day != d.day:
        same_day_next_year += timedelta(days=1)

    return same_day_next_year


class CalendarDrawing:

    def __init__(self, start_date=None, end_date=None, month_labels="left"):
        self.start_date = date.today() if start_date is None else start_date
        if end_date is None:
            # Default to one year, correcting for leap year.
            self.end_date = add_one_year(self.start_date)
        else:
            self.end_date = end_date

        self.month_labels = month_labels
        self.font = "Helvetica"
        self.font_month = "Helvetica-Bold"
        self.font_size = 12

    def weeks(self):
        d = self.start_date
        row = 0
        week = []
        while d != self.end_date:

            week.append(d)

            d += timedelta(days=1)
            if d.weekday() == 0:
                yield week
                week = []
                row += 1
                row_shows_month = False

        if week:
            yield week

    def draw(self, canvas, x, y):
        canvas.setFont(self.font, self.font_size)

        col_spacing = self.font_size * 2.0
        row_spacing = self.font_size * 1.7

        row_shows_month = False
        for row, week in enumerate(self.weeks()):
            row_shows_month = False
            for d in week:
                col = d.weekday()

                # Month Divisions
                # TODO: If the first row starts with the last day of the
                # month, the next month should probably take precedent
                # (assuming the first of the next month is on this row.
                if not row_shows_month and (d.day == 1 or row == 0):
                    row_shows_month = True

                    # Month Text
                    canvas.setFont(self.font_month, self.font_size)
                    canvas.setFillColor(get_month_color(d))
                    if self.month_labels == "left":
                        offset = col_spacing*(-1.5)
                    elif self.month_labels == "right":
                        offset = col_spacing*(1.5+6)
                    else:
                        raise ValueError("Invalid value for month_labels")
                    canvas.drawCentredString(
                        x + offset,
                        y - row_spacing*row,
                        d.strftime("%b")
                    )
                    canvas.setFont(self.font, self.font_size)

                    # Lines between months
                    #TODO: Some lines extraneous, like when first of month is
                    #      the first day of a week.
                    if row != 0:
                        canvas.setStrokeColor(COLOR_GRAY)
                        p = canvas.beginPath()
                        p.moveTo(
                            x - col_spacing/2,
                            y-row_spacing*row - row_spacing/4
                        )
                        p.lineTo(
                            x + col*col_spacing - col_spacing/2,
                            y-row_spacing*row - row_spacing/4
                        )
                        if col == 0:
                            p.moveTo(
                                x + col*col_spacing - col_spacing/2,
                                y-row_spacing*(row-1) - row_spacing/4
                            )
                        else:
                            p.lineTo(
                                x + col*col_spacing - col_spacing/2,
                                y-row_spacing*(row-1) - row_spacing/4
                            )
                        p.lineTo(
                            x + 7*col_spacing - col_spacing/2,
                            y-row_spacing*(row-1) - row_spacing/4
                        )
                        canvas.drawPath(p)

                # Draw Day of Month
                canvas.setFillColor(get_month_color(d))
                canvas.drawCentredString(
                    x + col_spacing*d.weekday(),
                    y - row_spacing*row,
                    str(d.day)
                )

    def split(self):
        left = copy(self)
        right = copy(self)

        weeks = list(self.weeks())
        last_week_in_left   = weeks[len(weeks)//2]
        first_week_in_right = weeks[len(weeks)//2 + 1]

        left.end_date = last_week_in_left[-1] + timedelta(days=1)
        right.start_date = first_week_in_right[0]
        left.month_labels = "left"
        right.month_labels = "right"

        return left, right

def generate_calendar(outfile, start_date=None):
    c = canvas.Canvas(outfile, pagesize=letter)
    w, h = letter

    if start_date is None:
        start_date = date.today()

    cal = CalendarDrawing(start_date)
    left_col, right_col = cal.split()
    left_col.draw(c, 125, h-180)
    right_col.draw(c, 350, h-180)

    c.showPage()
    c.save()


def main():
    generate_calendar(open("calendar.pdf", 'wb'))

if __name__ == "__main__":
    main()
