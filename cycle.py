from datetime import datetime, timedelta



def get_cycle():
    return "2407"


def get_cycle_download():
    return "2407"


def get_first_date(year):
    # Date for first cycle every year in January starting 2014
    first_dates = {
        2020: 2,
        2021: 28,
        2022: 27,
        2023: 26,
        2024: 25,
        2025: 23,
        2026: 22,
        2027: 21,
        2028: 20,
        2029: 18
    }
    return first_dates.get(year, 0)


def get_version_start(cycle_name):
    try:
        cycle = int(cycle_name)
    except ValueError:
        return ""

    cycle_upper = cycle // 100
    cycle_lower = cycle - (cycle_upper * 100)
    first_date = get_first_date(2000 + cycle_upper)
    if first_date < 1:
        return ""

    epoch = datetime(2000 + cycle_upper, 1, first_date, 9, 0, 0)
    epoch += timedelta(days=28 * (cycle_lower - 1))
    fmt1 = epoch.strftime("%m-%d-%Y")
    return f"{fmt1}"
