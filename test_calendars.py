
from datetime import date

from calgen import generate_calendar

def main():
    test_dates = [
        date(2017, 9, 6),    # Nothing Special
        date(2018, 3, 26),   # First row contains both 31st and 1st
        date(2017, 9, 22),   # Like prev, but on second column
        date(2019, 12, 31),  # Like prev, but on first column and boundary is a year
        date(2019, 4, 1),    # First row starts on Monday the 1st
    ]
    for d in test_dates:
        generate_calendar("test_{}.pdf".format(d.strftime("%Y-%m-%d")), d)
    generate_calendar("test_today.pdf", date.today())

if __name__ == "__main__":
    main()
