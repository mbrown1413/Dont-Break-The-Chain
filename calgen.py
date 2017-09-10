# Don't Break the Chain calendar
#
# Design based on:
# http://karenkavett.com/blog/3555/dont-break-the-chain-calendar-2017-free-motivational-tool-printable.php

from datetime import date, timedelta
from copy import copy

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter, A4


COLOR_BLACK = "#000000"
COLOR_GRAY = "#777777"

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

    def __init__(self, start_date=None, end_date=None, label_side="left"):
        self.start_date = date.today() if start_date is None else start_date
        if end_date is None:
            # Default to one year, correcting for leap year.
            self.end_date = add_one_year(self.start_date)
        else:
            self.end_date = end_date
        self.label_side = label_side
        self.font_size = 12

        self.col_spacing = self.font_size * 2.0
        self.row_spacing = self.font_size * 1.7

    def get_width(self):
        """Does not include side labels."""
        return self.col_spacing * 7

    def get_month_color(self, d):
        if (d.year*12 + d.month) % 2 == 0:
            return COLOR_BLACK
        else:
            return COLOR_GRAY

    def set_font_style(self, canvas, style, d):
        if style == "day":
            canvas.setFont("Helvetica", self.font_size)
            canvas.setFillColor(self.get_month_color(d))
        elif style == "month":
            canvas.setFont("Helvetica", self.font_size)
            canvas.setFillColor(self.get_month_color(d))
        elif style == "year":
            canvas.setFont("Helvetica", self.font_size*1.1)
            canvas.setFillColor(self.get_month_color(d))
        else:
            raise ValueError()

    def weeks(self):
        d = self.start_date
        row = 0
        week = []
        while d <= self.end_date:
            week.append(d)

            d += timedelta(days=1)
            if d.weekday() == 0:
                yield week
                week = []
                row += 1

        if week:
            yield week

    def draw(self, canvas, x, y, show_year_on_first_row=False):
        x += self.col_spacing/2
        y += self.row_spacing/2

        # Force the next row to be labeled
        # This happens when the first row is labeled, as usual, but also
        # contains the first day of the next month.
        force_label_next_row = False

        for row, week in enumerate(self.weeks()):
            row_shows_month = False
            row_shows_year = False

            # Draw row label?
            days_of_month = [d.day for d in week]
            if 1 in days_of_month or row == 0 or force_label_next_row:
                force_label_next_row = False
                if row == 0:
                    d = week[0]
                    force_label_next_row = 1 in days_of_month and d.day != 1
                elif 1 in days_of_month:
                    d = week[days_of_month.index(1)]
                else:  # force_label_next_row == true
                    d = week[0]
                force_show_year = row == 0 and show_year_on_first_row
                self.draw_row_label(canvas, x, y, d, row, force_show_year)

            # Draw month divider?
            if 1 in days_of_month:
                col = week[days_of_month.index(1)].weekday()
                self.draw_month_divider(canvas, x, y, row, col)

            # Days of Month
            for d in week:
                self.set_font_style(canvas, "day", d)
                canvas.drawCentredString(
                    x + self.col_spacing*d.weekday(),
                    y - self.row_spacing*row,
                    str(d.day)
                )

    def draw_row_label(self, canvas, x, y, d, row, force_show_year=False):
        """
        Draw month on the side. Also draws year if January, or if
        `force_show_year` is True.
        """

        # Month Text
        self.set_font_style(canvas, "month", d)
        if self.label_side == "left":
            offset = self.col_spacing*(-1.5)
        elif self.label_side == "right":
            offset = self.col_spacing*(1.5+6)
        else:
            raise ValueError("Invalid value for label_side")
        canvas.drawCentredString(
            x + offset,
            y - self.row_spacing*row,
            d.strftime("%b")
        )

        # Year Text
        if d.month == 1 or force_show_year:
            self.set_font_style(canvas, "year", d)
            if self.label_side == "left":
                offset = self.col_spacing*(-2.9)
            elif self.label_side == "right":
                offset = self.col_spacing*(2.9+6)
            else:
                raise ValueError("Invalid value for label_side")
            canvas.drawCentredString(
                x + offset,
                y - self.row_spacing*row,
                d.strftime("%Y")
            )

    def draw_month_divider(self, canvas, x, y, row, col):
        canvas.setStrokeColor(COLOR_GRAY)
        p = canvas.beginPath()
        p.moveTo(
            x - self.col_spacing/2,
            y-self.row_spacing*row - self.row_spacing/4
        )
        p.lineTo(
            x + col*self.col_spacing - self.col_spacing/2,
            y-self.row_spacing*row - self.row_spacing/4
        )
        if col == 0:
            p.moveTo(
                x + col*self.col_spacing - self.col_spacing/2,
                y-self.row_spacing*(row-1) - self.row_spacing/4
            )
        else:
            p.lineTo(
                x + col*self.col_spacing - self.col_spacing/2,
                y-self.row_spacing*(row-1) - self.row_spacing/4
            )
        p.lineTo(
            x + 7*self.col_spacing - self.col_spacing/2,
            y-self.row_spacing*(row-1) - self.row_spacing/4
        )
        canvas.drawPath(p)


    def split(self):
        left = copy(self)
        right = copy(self)

        weeks = list(self.weeks())
        last_week_in_left   = weeks[len(weeks)//2]
        first_week_in_right = weeks[len(weeks)//2 + 1]

        left.end_date = last_week_in_left[-1]
        right.start_date = first_week_in_right[0]
        left.label_side = "left"
        right.label_side = "right"

        return left, right

def generate_calendar(outfile, start_date=None):
    c = canvas.Canvas(outfile, pagesize=letter)
    c.setAuthor("Michael Brown")
    w, h = letter
    center = w / 2

    if start_date is None:
        start_date = date.today()

    cal = CalendarDrawing(start_date)
    left_col, right_col = cal.split()
    middle_padding = 50
    left_col.draw(c, center - middle_padding/2 - left_col.get_width(), h-195, show_year_on_first_row=True)
    right_col.draw(c, center + middle_padding/2 , h-195)

    # Title
    c.setFont("Helvetica", 30)
    c.setFillColor("black")
    c.drawCentredString(w/2, h-100, "_______________")

    # Subtitle
    date_format = "%b %d, %Y"
    subtitle = "{} - {}".format(
            left_col.start_date.strftime(date_format),
            right_col.end_date.strftime(date_format),
    )
    c.setFont("Helvetica", 12)
    c.setFillColor(COLOR_GRAY)
    c.drawCentredString(w/2, h-130, subtitle)

    # PDF title
    c.setTitle("Don't Break the Chain {}".format(subtitle))

    # Attribution
    #c.setFont("Helvetica", 10)
    #c.setFillColor(COLOR_GRAY)
    #c.drawCentredString(w/2 + 200, 42, "Michael Brown")

    # Lines for debugging alignment
    """
    p = c.beginPath()
    # Center
    p.moveTo(w/2, 72)
    p.lineTo(w/2, h-72)
    # Left
    p.moveTo(36, 72)
    p.lineTo(36, h-72)
    # Right
    p.moveTo(w-36, 72)
    p.lineTo(w-36, h-72)
    c.drawPath(p)
    """

    c.showPage()
    c.save()


def main():
    generate_calendar(open("calendar.pdf", 'wb'))

if __name__ == "__main__":
    main()
