import pandas as pd 
import re 
from datetime import datetime

def find_all_meeting_dates():
    date_file = "dates.txt"

    meeting_pattern = re.compile(r'^Meeting,\s+([A-Za-z]+)\s+(\d{1,2})(?:-\d{1,2})?,\s+(\d{4})')
    meeting_pattern_mult_month =  re.compile(r"^Meeting,\s+([A-Za-z]+)\s+(\d{1,2})-([A-Za-z]+)\s+(\d{1,2}),\s+(\d{4})")

    dates = []

    with open(date_file, "r") as f: 
        for line in f: 
            raw = line.strip()
            mult = False
            # check first regex parsing
            meeting = meeting_pattern.match(raw)

            # check second 
            if not meeting: 
                mult = True
                meeting = meeting_pattern_mult_month.match(raw)

            # is not a fed meeting 
            if not meeting: 
                continue
            if mult: 
                month_, day_, month, day, year = meeting.groups()
            else: 
                month, day, year = meeting.groups()
            str_date = f"{month} {day} {year}"

            date = datetime.strptime(str_date, "%B %d %Y").date()
            date = date.strftime("%Y-%m-%d")
            dates.append(date)


    df = pd.DataFrame(dates, columns=["date"])

    df["date"] = pd.to_datetime(df["date"])

    # f_date refers to the adjusted friday date
    df["f_date"] = df["date"] + pd.to_timedelta((4 - df["date"].dt.weekday) % 7, unit="D")
    df["f_date"] = df["f_date"].dt.strftime("%Y-%m-%d")

    #dates_csv = "all_meeting_dates.csv"

    #df.to_csv(dates_csv, index=False)

    return df 

